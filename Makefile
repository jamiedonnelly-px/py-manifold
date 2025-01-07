include .env

env: 
	@conda create -n ${CONDA_ENV_NAME} python=${PYTHON_VER}

rmenv:
	@conda remove --all -y -n ${CONDA_ENV_NAME}

install-packages:
	@pip install -r requirements.txt
	@pip install -ve . 

run-test:
	@python tests/run.py

clean:
	@rm -rf build
	@find . -name *.so | xargs -I {} rm -f {}
	@find . -name __pycache__ | xargs -I {} rm -rf {}
	@find . -name *.pyd | xargs -I {} rm -f {}
	@find . -name *.egg* | xargs -I {} rm -rf {}
