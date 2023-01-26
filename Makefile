# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

CLUSTER_NAME = collab-cluster
LOCAL_REGISTRY_NAME = localhost
CLUSTER_REGISTRY_NAME = myregistry.localhost
REGISTRY_PORT = 12345
RELEASE = dev
NAMESPACE = collab-manager
SESSION_NAMESPACE = collab-sessions
PORT ?= 8080

# List of Capella versions, e.g.: `5.0.0 5.2.0 6.0.0`
CAPELLA_VERSIONS ?= 5.2.0
# List of T4C versions, e.g., `5.2.0 6.0.0`
T4C_CLIENT_VERSIONS ?= 5.2.0

TIMEOUT ?= 10m

CAPELLA_DOCKERIMAGES = $(MAKE) -C capella-dockerimages PUSH_IMAGES=1 DOCKER_REGISTRY=$(LOCAL_REGISTRY_NAME):$(REGISTRY_PORT)

# Adds support for msys
export MSYS_NO_PATHCONV := 1

# Use Docker Buildkit on Linux
export DOCKER_BUILDKIT=1

.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS = -euo pipefail -c

build: backend frontend docs guacamole

backend: IMAGE=capella/collab/backend
backend:
	python backend/generate_git_archival.py;
	docker build -t $(IMAGE) -t $(LOCAL_REGISTRY_NAME):$(REGISTRY_PORT)/$(IMAGE) backend
	docker push $(LOCAL_REGISTRY_NAME):$(REGISTRY_PORT)/$(IMAGE)

frontend: IMAGE=capella/collab/frontend
frontend:
	node frontend/fetch-version.ts
	docker build --build-arg CONFIGURATION=local -t $(IMAGE) -t $(LOCAL_REGISTRY_NAME):$(REGISTRY_PORT)/$(IMAGE) frontend
	docker push $(LOCAL_REGISTRY_NAME):$(REGISTRY_PORT)/$(IMAGE)

guacamole: IMAGE=capella/collab/guacamole
guacamole:
	docker build -t $(IMAGE) -t $(LOCAL_REGISTRY_NAME):$(REGISTRY_PORT)/$(IMAGE) guacamole
	docker push $(LOCAL_REGISTRY_NAME):$(REGISTRY_PORT)/$(IMAGE)

capella:
	$(CAPELLA_DOCKERIMAGES) CAPELLA_VERSIONS="$(CAPELLA_VERSIONS)" capella/remote capella/readonly

t4c-client:
	$(CAPELLA_DOCKERIMAGES) CAPELLA_VERSIONS="$(T4C_CLIENT_VERSIONS)" t4c/client/remote t4c/client/backup

docs:
	docker build -t capella/collab/docs -t $(LOCAL_REGISTRY_NAME):$(REGISTRY_PORT)/capella/collab/docs docs/user
	docker push $(LOCAL_REGISTRY_NAME):$(REGISTRY_PORT)/capella/collab/docs

deploy: build capella helm-deploy open rollout

# Deploy with full T4C client support:
deploy-t4c: build t4c-client helm-deploy open rollout

deploy-without-build: helm-deploy open rollout

helm-deploy:
	@k3d cluster list $(CLUSTER_NAME) >/dev/null || $(MAKE) create-cluster
	@kubectl create namespace $(SESSION_NAMESPACE) 2> /dev/null || true
	@helm dependency update ./helm
	@helm upgrade --install \
		--kube-context k3d-$(CLUSTER_NAME) \
		--create-namespace \
		--namespace $(NAMESPACE) \
		--values helm/values.yaml \
		$$(test -f secrets.yaml && echo "--values secrets.yaml") \
		--set docker.registry.internal=k3d-$(CLUSTER_REGISTRY_NAME):$(REGISTRY_PORT) \
		--set docker.images.guacamole.guacamole=k3d-$(CLUSTER_REGISTRY_NAME):$(REGISTRY_PORT)/capella/collab/guacamole \
		--set mocks.oauth=True \
		--set target=local \
		--set general.port=8080 \
		--set backend.k8sSessionNamespace="$(SESSION_NAMESPACE)" \
		--set backend.authentication.oauth.redirectURI="http://localhost:$(PORT)/oauth2/callback" \
		--set backend.authentication.oauth.endpoints.wellKnown="http://$(RELEASE)-oauth-mock:8080/default/.well-known/openid-configuration" \
		$(RELEASE) ./helm
	$(MAKE) provision-guacamole wait

open:
	@export URL=http://localhost:8080; \
	if [ "Windows_NT" = "$(OS)" ]; \
	then \
		start "$$URL"; \
	elif [ "$(shell uname -s)" = "Linux" ]; \
	then \
		xdg-open "$$URL"; \
	elif [ "$(shell uname -s)" = "Darwin" ]; \
	then \
		open "$$URL"; \
	fi

clear-backend-db:
	kubectl delete deployment -n $(NAMESPACE) $(RELEASE)-backend-postgres
	kubectl delete pvc -n $(NAMESPACE) $(RELEASE)-volume-backend-postgres
	$(MAKE) helm-deploy

rollout:
	kubectl --context k3d-$(CLUSTER_NAME) rollout restart deployment -n $(NAMESPACE) $(RELEASE)-backend
	kubectl --context k3d-$(CLUSTER_NAME) rollout restart deployment -n $(NAMESPACE) $(RELEASE)-frontend
	kubectl --context k3d-$(CLUSTER_NAME) rollout restart deployment -n $(NAMESPACE) $(RELEASE)-docs

undeploy:
	kubectl --context k3d-$(CLUSTER_NAME) delete namespace $(SESSION_NAMESPACE) $(NAMESPACE)

registry:
	type k3d || { echo "K3D is not installed, install k3d and run 'make create-cluster' again"; exit 1; }
	k3d registry list $(CLUSTER_REGISTRY_NAME) 2>&- || k3d registry create $(CLUSTER_REGISTRY_NAME) --port $(REGISTRY_PORT)

create-cluster: registry
	k3d cluster list $(CLUSTER_NAME) 2>&- || k3d cluster create $(CLUSTER_NAME) \
		--registry-use k3d-$(CLUSTER_REGISTRY_NAME):$(REGISTRY_PORT) \
		--port "8080:80@loadbalancer"
	kubectl cluster-info
	kubectl config set-context --current --namespace=$(NAMESPACE)

delete-cluster:
	k3d cluster list $(CLUSTER_NAME) 2>&- && k3d cluster delete $(CLUSTER_NAME)

wait:
	@echo "-----------------------------------------------------------"
	@echo "--- Please wait until all services are in running state ---"
	@echo "-----------------------------------------------------------"
	@(kubectl get --context k3d-$(CLUSTER_NAME) -n $(NAMESPACE) --watch pods) &
	@kubectl wait --context k3d-$(CLUSTER_NAME) --all deployment --for condition=Available=True --timeout=$(TIMEOUT)
	@kill %%

provision-guacamole:
	@echo "Waiting for guacamole container, before we can initialize the database..."
	@kubectl get -n $(NAMESPACE) --watch pods &
	@sleep 2
	@kubectl wait --for=condition=Ready pods --timeout=$(TIMEOUT) --context k3d-$(CLUSTER_NAME) -n $(NAMESPACE) -l id=$(RELEASE)-deployment-guacamole-guacamole
	@kubectl wait --for=condition=Ready pods --timeout=$(TIMEOUT) --context k3d-$(CLUSTER_NAME) -n $(NAMESPACE) -l id=$(RELEASE)-deployment-guacamole-postgres
	@kill %%
	@kubectl exec --context k3d-$(CLUSTER_NAME) --namespace $(NAMESPACE) --container $(RELEASE)-guacamole-guacamole deployment/$(RELEASE)-guacamole-guacamole -- /opt/guacamole/bin/initdb.sh --postgres | \
	kubectl exec -i --context k3d-$(CLUSTER_NAME) --namespace $(NAMESPACE) deployment/$(RELEASE)-guacamole-postgres -- psql -U guacamole guacamole
	@echo "Guacamole database initialized sucessfully.";

# Execute with `make -j3 dev`
dev: dev-oauth-mock dev-frontend dev-backend

dev-frontend:
	$(MAKE) -C frontend dev

dev-backend:
	$(MAKE) -C backend dev

dev-oauth-mock:
	$(MAKE) -C mocks/oauth start

backend-logs:
	kubectl logs -f -n $(NAMESPACE) -l id=$(RELEASE)-deployment-backend

context:
	kubectl config set-context k3d-$(CLUSTER_NAME) --namespace=$(NAMESPACE)

dashboard:
	kubectl apply --context k3d-$(CLUSTER_NAME) -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.5.0/aio/deploy/recommended.yaml
	kubectl apply -f dashboard/dashboard.rolebinding.yml -f dashboard/dashboard.serviceaccount.yml
	echo "Please open the portal: http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/#/login"
	echo "Please use the following token: $$(kubectl -n default create token dashboard-admin)"
	kubectl proxy

.PHONY: *
