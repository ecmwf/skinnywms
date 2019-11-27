# test command
TEST_CMD := python /app/skinnywms/demo.py --host='0.0.0.0' --port=5000

# load variables from ./hooks/env
MAGICS_IMAGE := ${shell . ./hooks/env && echo $$MAGICS_IMAGE}
DATE := ${shell . ./hooks/env && echo $$DATE}
SOURCE_URL := ${shell . ./hooks/env && echo $$SOURCE_URL}
SOURCE_BRANCH := ${shell . ./hooks/env && echo $$SOURCE_BRANCH}
SOURCE_COMMIT := ${shell . ./hooks/env && echo $$SOURCE_COMMIT}
SOURCE_TAG := ${shell . ./hooks/env && echo $$SOURCE_TAG}
DOCKER_TAG := ${shell . ./hooks/env && echo $$DOCKER_TAG}
IMAGE_NAME := ${shell . ./hooks/env && echo $$IMAGE_NAME}

all: deploy

.PHONY: key deploy login build test push

key:
	python3 -m keyring set https://upload.pypi.org/legacy/ SylvieLamy-Thepaut

deploy:
	rm -fR dist buil skinnywms.egg-info/
	python3 setup.py sdist bdist_wheel
	python3 -m twine upload --verbose --repository-url https://upload.pypi.org/legacy/ dist/* -u SylvieLamy-Thepaut

login:
	docker login

build:
	./hooks/build

test:
	docker run --rm -p 5000:5000 -i -t ${IMAGE_NAME} ${TEST_CMD}

push: login
	@docker push ${DOCKER_REPO}