

all: deploy


key:
	python3 -m keyring set https://upload.pypi.org/legacy/ SylvieLamy-Thepaut

deploy:
	rm -fR dist buil skinnywms.egg-info/
	python3 setup.py sdist bdist_wheel
	python3 -m twine upload --verbose --repository-url https://upload.pypi.org/legacy/ dist/* -u SylvieLamy-Thepaut

