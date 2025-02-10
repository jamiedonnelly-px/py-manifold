import copy
from dataclasses import dataclass
import heapq

import numpy as np
import numpy.typing as npt
import pyvista as pv

from manifold import _faces_to_1d, _faces_to_2d

@dataclass(kw_only=True)
class _MeshSimplifier:
    def __init__(self, mesh: pv.PolyData, reduction: float = 0.5, valence_aware: bool = True, midpoint: bool = True, valence_params: tuple[int] = (6, 1)):
        self.vs, self.faces = mesh.points, _faces_to_2d(mesh.faces)
        self.target_n_verts = int(mesh.n_points * reduction)
        self.valence_aware = valence_aware,
        self.midpoint = midpoint,
        self._optim_valence, self._valence_weight = valence_params
        self.compute_face_normals()
        self.compute_face_center()
        self.build_gemm()
        self.build_v2v()
        self.build_vf()

    def build_gemm(self):
        # TODO: Implement distance-based edges for non-manifold multi-component meshes.
        self.ve = [[] for _ in self.vs]
        self.vei = [[] for _ in self.vs]
        edge_nb = []
        sides = []
        edge2key = dict()
        edges = []
        edges_count = 0
        nb_count = []
        for face_id, face in enumerate(self.faces):
            faces_edges = []
            for i in range(3):
                cur_edge = (face[i], face[(i + 1) % 3])
                faces_edges.append(cur_edge)
            for idx, edge in enumerate(faces_edges):
                edge = tuple(sorted(list(edge)))
                faces_edges[idx] = edge
                if edge not in edge2key:
                    edge2key[edge] = edges_count
                    edges.append(list(edge))
                    edge_nb.append([-1, -1, -1, -1])
                    sides.append([-1, -1, -1, -1])
                    self.ve[edge[0]].append(edges_count)
                    self.ve[edge[1]].append(edges_count)
                    self.vei[edge[0]].append(0)
                    self.vei[edge[1]].append(1)
                    nb_count.append(0)
                    edges_count += 1
            for idx, edge in enumerate(faces_edges):
                edge_key = edge2key[edge]
                edge_nb[edge_key][nb_count[edge_key]] = edge2key[faces_edges[(idx + 1) % 3]]
                edge_nb[edge_key][nb_count[edge_key] + 1] = edge2key[faces_edges[(idx + 2) % 3]]
                nb_count[edge_key] += 2
            for idx, edge in enumerate(faces_edges):
                edge_key = edge2key[edge]
                sides[edge_key][nb_count[edge_key] - 2] = nb_count[edge2key[faces_edges[(idx + 1) % 3]]] - 1
                sides[edge_key][nb_count[edge_key] - 1] = nb_count[edge2key[faces_edges[(idx + 2) % 3]]] - 2
        self.edges = np.array(edges, dtype=np.int32)
        self.gemm_edges = np.array(edge_nb, dtype=np.int64)
        self.sides = np.array(sides, dtype=np.int64)
        self.edges_count = edges_count

    def compute_face_normals(self):
        face_normals = np.cross(self.vs[self.faces[:, 1]] - self.vs[self.faces[:, 0]], self.vs[self.faces[:, 2]] - self.vs[self.faces[:, 0]])
        norm = np.linalg.norm(face_normals, axis=1, keepdims=True) + 1e-24
        face_areas = 0.5 * np.sqrt((face_normals**2).sum(axis=1))
        face_normals /= norm
        self.fn, self.fa = face_normals, face_areas
    
    def compute_face_center(self):
        faces = self.faces
        vs = self.vs
        self.fc = np.sum(vs[faces], 1) / 3.0
    
    def build_vf(self):
        vf = [set() for _ in range(len(self.vs))]
        for i, f in enumerate(self.faces):
            vf[f[0]].add(i)
            vf[f[1]].add(i)
            vf[f[2]].add(i)
        self.vf = vf

    def build_v2v(self):
        v2v = [[] for _ in range(len(self.vs))]
        for i, e in enumerate(self.edges):
            v2v[e[0]].append(e[1])
            v2v[e[1]].append(e[0])
        self.v2v = v2v

    def simplification(self) -> tuple[npt.NDArray[np.float64]]:
        vs, vf, fn, fc, edges = self.vs, self.vf, self.fn, self.fc, self.edges

        """ 1. compute Q for each vertex """
        Q_s = [[] for _ in range(len(vs))]
        E_s = [[] for _ in range(len(vs))]
        for i, v in enumerate(vs):
            f_s = np.array(list(vf[i]))
            fc_s = fc[f_s]
            fn_s = fn[f_s]
            d_s = - 1.0 * np.sum(fn_s * fc_s, axis=1, keepdims=True)
            abcd_s = np.concatenate([fn_s, d_s], axis=1)
            Q_s[i] = np.matmul(abcd_s.T, abcd_s)
            v4 = np.concatenate([v, np.array([1])])
            E_s[i] = np.matmul(v4, np.matmul(Q_s[i], v4.T))

        """ 2. compute E for every possible pairs and create heapq """
        E_heap = []
        for i, e in enumerate(edges):
            v_0, v_1 = vs[e[0]], vs[e[1]]
            Q_0, Q_1 = Q_s[e[0]], Q_s[e[1]]
            Q_new = Q_0 + Q_1

            if self.midpoint:
                v_new = 0.5 * (v_0 + v_1)
                v4_new = np.concatenate([v_new, np.array([1])])
            else:
                Q_lp = np.eye(4)
                Q_lp[:3] = Q_new[:3]
                try:
                    Q_lp_inv = np.linalg.inv(Q_lp)
                    v4_new = np.matmul(Q_lp_inv, np.array([[0,0,0,1]]).reshape(-1,1)).reshape(-1)
                except:
                    print(f"Failed to compute inverse matrix: {Q_lp}")
                    v_new = 0.5 * (v_0 + v_1)
                    v4_new = np.concatenate([v_new, np.array([1])])

            valence_penalty = 1
            if self.valence_aware:
                merged_faces = vf[e[0]].intersection(vf[e[1]])
                valence_new = len(vf[e[0]].union(vf[e[1]]).difference(merged_faces))
                valence_penalty = self.valence_weight(valence_new)
            
            E_new = np.matmul(v4_new, np.matmul(Q_new, v4_new.T)) * valence_penalty
            heapq.heappush(E_heap, (E_new, (e[0], e[1])))

        """ 3. collapse minimum-error vertex """
        simp_mesh = copy.deepcopy(self)

        vi_mask = np.ones([len(simp_mesh.vs)]).astype(np.bool_)
        fi_mask = np.ones([len(simp_mesh.faces)]).astype(np.bool_)

        vert_map = [{i} for i in range(len(simp_mesh.vs))]
        while np.sum(vi_mask) > self.target_n_verts:
            if len(E_heap) == 0:
                print("[Warning]: edge cannot be collapsed anymore!")
                break

            E_0, (vi_0, vi_1) = heapq.heappop(E_heap)

            if (vi_mask[vi_0] == False) or (vi_mask[vi_1] == False):
                continue

            """ edge collapse """
            shared_vv = list(set(simp_mesh.v2v[vi_0]).intersection(set(simp_mesh.v2v[vi_1])))
            merged_faces = simp_mesh.vf[vi_0].intersection(simp_mesh.vf[vi_1])

            if len(shared_vv) != 2:
                """ non-manifold! """
                continue

            elif len(merged_faces) != 2:
                """ boundary """
                continue

            else:
                self.edge_collapse(simp_mesh, vi_0, vi_1, merged_faces, vi_mask, fi_mask, vert_map, Q_s, E_heap, valence_aware=valence_aware)
        
        self.rebuild_mesh(simp_mesh, vi_mask, fi_mask, vert_map)
        return simp_mesh.vs, simp_mesh.faces
    
    def edge_collapse(self, simp_mesh, vi_0, vi_1, merged_faces, vi_mask, fi_mask, vert_map, Q_s, E_heap, valence_aware):
        shared_vv = list(set(simp_mesh.v2v[vi_0]).intersection(set(simp_mesh.v2v[vi_1])))
        new_vi_0 = set(simp_mesh.v2v[vi_0]).union(set(simp_mesh.v2v[vi_1])).difference({vi_0, vi_1})
        simp_mesh.vf[vi_0] = simp_mesh.vf[vi_0].union(simp_mesh.vf[vi_1]).difference(merged_faces)
        simp_mesh.vf[vi_1] = set()
        simp_mesh.vf[shared_vv[0]] = simp_mesh.vf[shared_vv[0]].difference(merged_faces)
        simp_mesh.vf[shared_vv[1]] = simp_mesh.vf[shared_vv[1]].difference(merged_faces)

        simp_mesh.v2v[vi_0] = list(new_vi_0)
        for v in simp_mesh.v2v[vi_1]:
            if v != vi_0:
                simp_mesh.v2v[v] = list(set(simp_mesh.v2v[v]).difference({vi_1}).union({vi_0}))
        simp_mesh.v2v[vi_1] = []
        vi_mask[vi_1] = False

        vert_map[vi_0] = vert_map[vi_0].union(vert_map[vi_1])
        vert_map[vi_0] = vert_map[vi_0].union({vi_1})
        vert_map[vi_1] = set()
        
        fi_mask[np.array(list(merged_faces)).astype(np.int32)] = False

        simp_mesh.vs[vi_0] = 0.5 * (simp_mesh.vs[vi_0] + simp_mesh.vs[vi_1])

        """ recompute E """
        Q_0 = Q_s[vi_0]
        for vv_i in simp_mesh.v2v[vi_0]:
            v_mid = 0.5 * (simp_mesh.vs[vi_0] + simp_mesh.vs[vv_i])
            Q_1 = Q_s[vv_i]
            Q_new = Q_0 + Q_1
            v4_mid = np.concatenate([v_mid, np.array([1])])

            valence_penalty = 1
            if valence_aware:
                merged_faces = simp_mesh.vf[vi_0].intersection(simp_mesh.vf[vv_i])
                valence_new = len(simp_mesh.vf[vi_0].union(simp_mesh.vf[vv_i]).difference(merged_faces))
                valence_penalty = self.valence_weight(valence_new)

            E_new = np.matmul(v4_mid, np.matmul(Q_new, v4_mid.T)) * valence_penalty
            heapq.heappush(E_heap, (E_new, (vi_0, vv_i)))

    def valence_weight(self, valence_new):
        valence_penalty = abs(valence_new - self._optim_valence) * self._valence_weight + 1
        if valence_new == 3:
            valence_penalty *= 100000
        return valence_penalty      
    
    @staticmethod
    def rebuild_mesh(simp_mesh, vi_mask, fi_mask, vert_map):
        face_map = dict(zip(np.arange(len(vi_mask)), np.cumsum(vi_mask)-1))
        simp_mesh.vs = simp_mesh.vs[vi_mask]
        
        vert_dict = {}
        for i, vm in enumerate(vert_map):
            for j in vm:
                vert_dict[j] = i

        for i, f in enumerate(simp_mesh.faces):
            for j in range(3):
                if f[j] in vert_dict:
                    simp_mesh.faces[i][j] = vert_dict[f[j]]

        simp_mesh.faces = simp_mesh.faces[fi_mask]
        for i, f in enumerate(simp_mesh.faces):
            for j in range(3):
                simp_mesh.faces[i][j] = face_map[f[j]]
        return simp_mesh

def simplify(mesh: pv.PolyData, reduction: float = 0.5, valence_aware: bool = True, midpoint: bool = True, valence_params: tuple[int] = (6, 1)) -> pv.PolyData:
    """Function for simplifying an input mesh 

    Args:
        mesh (pv.PolyData): Input mesh
        reduction (float, optional): Fraction of verts to remove. Defaults to 0.5.
        valence_aware (bool, optional): Whether to implement valence-aware decimation. Defaults to True.
        midpoint (bool, optional): Whether to collapse (v1, v2) -> (v1 + v2)/2; or to optimise the position. Defaults to True.
        valence_params (tuple[int], optional): Parameters for valence weighting. Defaults to (6, 1).

    Returns:
        pv.PolyData: Simplified mesh.
    """
    if not(mesh.is_manifold):
        raise ValueError("Input mesh must be manifold.")

    mesh: _MeshSimplifier = _MeshSimplifier(mesh = mesh, \
                reduction = reduction, \
                valence_aware = valence_aware, \
                midpoint = midpoint, \
                valence_params = valence_params
            )
    
    simplified_verts, simplified_faces = mesh.simplification()

    return pv.PolyData(simplified_verts, _faces_to_1d(simplified_faces))