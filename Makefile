NAME := snapms
VERSION := $(shell poetry version --short)
REGISTRY := ghcr.io/liningtonlab

all: build-docker push

build-docker:
	docker build -t $(NAME):$(VERSION) -t $(NAME):latest .

push:
	docker tag $(NAME):$(VERSION) $(REGISTRY)/$(NAME):$(VERSION)
	docker push $(REGISTRY)/$(NAME):$(VERSION)

echo-name:
	echo $(REGISTRY)/$(NAME):$(VERSION)

test:
	pytest

format:
	isort snapms
	black snapms