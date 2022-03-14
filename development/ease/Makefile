#!make
include .env
export

local: 
	docker build -t t4c/client/ease/remote --build-arg BASE_IMAGE=t4c/client/ease capella-dockerimages/remote
	docker stop ease-debug
	docker rm ease-debug
	docker run -d \
		--name ease-debug \
		-p $(EASE_DEBUG_PORT):3389 \
		-v $(shell pwd)/local/scripts:/opt/scripts \
		-v $(shell pwd)/capella-dockerimages/ease/pyease:/opt/pyease \
		-e PYTHONPATH="/opt/pyease" \
		--env-file ./local/.env \
		t4c/client/ease/remote
	docker logs --follow ease-debug

deploy: 
	helm upgrade --install \
		--kube-context $(CONTEXT) \
		--create-namespace \
		--namespace $(NAMESPACE) \
		--values helm/secret.yaml \
		--wait --timeout 4m \
		--debug \
		$(RELEASE) ./helm

undeploy: 
	helm uninstall \
		--kube-context $(CONTEXT) \
		--namespace $(NAMESPACE) \
		$(RELEASE)