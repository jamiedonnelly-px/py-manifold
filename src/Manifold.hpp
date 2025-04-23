#ifndef MANIFOLD2_MANIFOLD_H_
#define MANIFOLD2_MANIFOLD_H_

#include <tuple>

#include "types.hpp"
#include "Octree.hpp"
#include "utils.hpp"

class Manifold {
public:
	Manifold();
	~Manifold();
	std::tuple<MatrixD, MatrixI> ProcessManifold(const MatrixD& verts, const MatrixI& faces, int depth, int verbose = 0);

protected:
	void BuildTree(int resolution, int verbose);
	void CalcBoundingBox();
	void ConstructManifold(int verbose);
	bool SplitGrid(const std::vector<Vector4i>& nface_indices,
		std::map<GridIndex,int>& vcolor,
		std::vector<Vector3>& nvertices,
		std::vector<std::set<int> >& v_faces,
		std::vector<Vector3i>& triangles);

private:	
	Octree* tree_;
	Vector3 min_corner_, max_corner_;
	MatrixD V_;
	MatrixI F_;

	std::vector<Vector3> vertices_;
	std::vector<Vector3i> face_indices_;
	std::vector<GridIndex > v_info_;

};

#endif