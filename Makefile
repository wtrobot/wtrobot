PACKAGE_NAME ?= wtrobot
PUSH_TO ?= pypi

.PHONY: version build push build-push local localdev clean
	
version:
	./package_version.sh ${PUSH_TO} ${PACKAGE_NAME}

build:
	python setup.py sdist bdist_wheel

push:
	twine upload --verbose --repository ${PUSH_TO} dist/*

build-push:
	$(MAKE) clean
	$(MAKE) version
	$(MAKE) build
	$(MAKE) push

local:
	$(MAKE) clean
	$(MAKE) version
	pip install .

localdev:
	$(MAKE) clean
	$(MAKE) version
	pip install -e .

clean:
	rm -rf setup.py build dist
