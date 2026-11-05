VERSION=v1
DOCKERUSER=thgh9905

build:
	docker build -f Dockerfile-rest -t demucs-rest .

push:
	docker tag demucs-rest $(DOCKERUSER)/demucs-rest:$(VERSION)
	docker push $(DOCKERUSER)/demucs-rest:$(VERSION)
	docker tag demucs-rest $(DOCKERUSER)/demucs-rest:latest
	docker push $(DOCKERUSER)/demucs-rest:latest
