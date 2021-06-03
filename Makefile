NAME := snapms
# VERSION := $(shell git describe --tags)
VERSION := 0.1.0
REGISTRY := registry.jvansan.duckdns.org

all: build-docker push

build-docker:
	docker build -t $(NAME):$(VERSION) -t $(NAME):latest .

push:
	docker tag $(NAME):$(VERSION) $(REGISTRY)/$(NAME):$(VERSION)
	docker push $(REGISTRY)/$(NAME):$(VERSION)

echo-name:
	echo $(REGISTRY)/$(NAME):$(VERSION)