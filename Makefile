include .env

.PHONY: install-package lint

env: 
	@conda create -n ${CONDA_ENV_NAME} python=${PYTHON_VER}

rmenv:
	@conda remove --all -y -n ${CONDA_ENV_NAME}

install-package:
	@pip install -v . 

install-package-test:
	@pip install -v ".[test]"

test:
	@pytest --verbose

generate-samples: install-package
	@python tests/generate_samples.py

lint:
	@echo "Running Ruff and Isort..."
	@ruff format .
	@ruff check . --fix
	@isort .

clean:
	@rm -rf build
	@find . -name *.so | xargs -I {} rm -f {}
	@find . -name __pycache__ | xargs -I {} rm -rf {}
	@find . -name *.pyd | xargs -I {} rm -f {}
	@find . -name *.egg* | xargs -I {} rm -rf {}
