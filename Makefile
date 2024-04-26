# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

CLUSTER_NAME = collab-cluster

RELEASE = dev
NAMESPACE = collab-manager
SESSION_NAMESPACE = collab-sessions

K3D_REGISTRY_PORT = 12345
K3D_REGISTRY_NAME = myregistry.localhost

DOCKER_REGISTRY ?= k3d-$(K3D_REGISTRY_NAME):$(K3D_REGISTRY_PORT)
CAPELLACOLLAB_SESSIONS_REGISTRY ?= $(DOCKER_REGISTRY)

# List of Capella versions, e.g.: `5.0.0 5.2.0 6.0.0`
CAPELLA_VERSIONS ?= 6.0.0
# List of T4C versions, e.g., `5.2.0 6.0.0`
T4C_CLIENT_VERSIONS ?= 6.0.0

DEVELOPMENT_MODE ?= 0

TIMEOUT ?= 10m

CAPELLA_DOCKERIMAGES = $(MAKE) -C capella-dockerimages PUSH_IMAGES=1 DOCKER_REGISTRY=$(DOCKER_REGISTRY)

# Adds support for msys
export MSYS_NO_PATHCONV := 1

# Use Docker Buildkit on Linux
export DOCKER_BUILDKIT=1

CREATE_ENV_FILE:=$(shell touch .env)
include .env

.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS = -euo pipefail -c

build: backend frontend docs guacamole jupyter session-preparation

backend: IMAGE=capella/collab/backend
backend:
	python backend/generate_git_archival.py;
	docker build -t $(IMAGE) -t $(DOCKER_REGISTRY)/$(IMAGE) backend
	docker push $(DOCKER_REGISTRY)/$(IMAGE)

frontend: IMAGE=capella/collab/frontend
frontend:
	python frontend/fetch-version.py
	docker build -t $(IMAGE) -t $(DOCKER_REGISTRY)/$(IMAGE) frontend
	docker push $(DOCKER_REGISTRY)/$(IMAGE)

guacamole: IMAGE=capella/collab/guacamole
guacamole:
	docker build -t $(IMAGE) -t $(DOCKER_REGISTRY)/$(IMAGE) images/guacamole
	docker push $(DOCKER_REGISTRY)/$(IMAGE)

session-preparation: IMAGE=capella/collab/session-preparation
session-preparation:
	docker build -t $(IMAGE) -t $(DOCKER_REGISTRY)/$(IMAGE) images/session-preparation
	docker push $(DOCKER_REGISTRY)/$(IMAGE)

capella:
	$(CAPELLA_DOCKERIMAGES) CAPELLA_VERSIONS="$(CAPELLA_VERSIONS)" capella/remote

t4c-client:
	$(CAPELLA_DOCKERIMAGES) CAPELLA_VERSIONS="$(T4C_CLIENT_VERSIONS)" t4c/client/remote

jupyter:
	$(CAPELLA_DOCKERIMAGES) jupyter-notebook

docs:
	docker build -t capella/collab/docs -t $(DOCKER_REGISTRY)/capella/collab/docs docs
	docker push $(DOCKER_REGISTRY)/capella/collab/docs

deploy: build capella helm-deploy rollout open

# Deploy with full T4C client support:
deploy-t4c: build t4c-client helm-deploy rollout open

deploy-without-build: helm-deploy rollout open

helm-deploy:
	@k3d cluster list $(CLUSTER_NAME) >/dev/null || $(MAKE) create-cluster
	@kubectl create namespace $(SESSION_NAMESPACE) 2> /dev/null || true
	@echo "Start helm upgrade..."
	@helm upgrade --install \
		--kube-context k3d-$(CLUSTER_NAME) \
		--create-namespace \
		--namespace $(NAMESPACE) \
		--values helm/values.yaml \
		$$(test -f secrets.yaml && echo "--values secrets.yaml") \
		--set docker.registry.internal=$(DOCKER_REGISTRY)/capella/collab \
		--set docker.registry.sessions=$(CAPELLACOLLAB_SESSIONS_REGISTRY) \
		--set docker.tag=latest \
		--set mocks.oauth=True \
		--set development=$(DEVELOPMENT_MODE) \
		--set cluster.ingressClassName=traefik \
		--set cluster.ingressNamespace=kube-system \
		--set backend.k8sSessionNamespace="$(SESSION_NAMESPACE)" \
		$(RELEASE) ./helm
	$(MAKE) provision-guacamole wait

open:
	@export URL=$$(helm show values helm --jsonpath '{.general.scheme}://{.general.host}:{.general.port}'); \
	if [ "Windows_NT" = "$(OS)" ] && command -v start > /dev/null; \
	then \
		start "$$URL"; \
	elif [ "$(shell uname -s)" = "Linux" ] && command -v xdg-open > /dev/null; \
	then \
		xdg-open "$$URL"; \
	elif [ "$(shell uname -s)" = "Darwin" ] && command -v open > /dev/null; \
	then \
		open "$$URL"; \
	fi

clear-backend-db:
	kubectl delete deployment -n $(NAMESPACE) $(RELEASE)-backend-postgres
	kubectl delete pvc -n $(NAMESPACE) $(RELEASE)-volume-backend-postgres
	$(MAKE) helm-deploy

rollout:
	DEPLOYMENTS="backend frontend docs guacamole-guacamole"

	for deployment in $$DEPLOYMENTS; do \
		kubectl --context k3d-$(CLUSTER_NAME) rollout restart deployment -n $(NAMESPACE) $(RELEASE)-$$deployment; \
	done

	for deployment in $$DEPLOYMENTS; do \
		kubectl --context k3d-$(CLUSTER_NAME) rollout status --timeout=5m deployment $(RELEASE)-$$deployment; \
	done

undeploy:
	kubectl --context k3d-$(CLUSTER_NAME) delete namespace $(SESSION_NAMESPACE) $(NAMESPACE)

registry:
	type k3d || { echo "K3D is not installed, install k3d and run 'make create-cluster' again"; exit 1; }
	k3d registry list $(K3D_REGISTRY_NAME) 2>&- || k3d registry create $(K3D_REGISTRY_NAME) --port $(K3D_REGISTRY_PORT)

create-cluster: registry
	k3d cluster list $(CLUSTER_NAME) 2>&- || k3d cluster create $(CLUSTER_NAME) \
		--registry-use k3d-$(K3D_REGISTRY_NAME):$(K3D_REGISTRY_PORT) \
		-p "8080:80@loadbalancer" \
		-p "443:443@loadbalancer" \
		-p "30000-30005:30000-30005@server:0"
	kubectl cluster-info
	kubectl config set-context --current --namespace=$(NAMESPACE)

delete-cluster:
	k3d cluster list $(CLUSTER_NAME) 2>&- && k3d cluster delete $(CLUSTER_NAME)

delete-registry:
	k3d registry list $(K3D_REGISTRY_NAME) 2>&- && k3d registry delete $(K3D_REGISTRY_NAME)

wait:
	@echo "-----------------------------------------------------------"
	@echo "--- Please wait until all services are in running state ---"
	@echo "-----------------------------------------------------------"
	@(kubectl get --context k3d-$(CLUSTER_NAME) -n $(NAMESPACE) --watch pods) &
	@kubectl wait --context k3d-$(CLUSTER_NAME) --all deployment --for condition=Available=True --timeout=$(TIMEOUT)
	@kill %%

provision-guacamole:
	@echo "Waiting for guacamole container, before we can initialize the database..."
	@kubectl get --context k3d-$(CLUSTER_NAME) -n $(NAMESPACE) --watch pods &
	@sleep 2
	@kubectl wait --for=condition=Ready pods --timeout=$(TIMEOUT) --context k3d-$(CLUSTER_NAME) -n $(NAMESPACE) -l id=$(RELEASE)-deployment-guacamole-guacamole
	@kubectl wait --for=condition=Ready pods --timeout=$(TIMEOUT) --context k3d-$(CLUSTER_NAME) -n $(NAMESPACE) -l id=$(RELEASE)-deployment-guacamole-postgres
	@kill %%
	@kubectl exec --context k3d-$(CLUSTER_NAME) --namespace $(NAMESPACE) --container $(RELEASE)-guacamole-guacamole deployment/$(RELEASE)-guacamole-guacamole -- /opt/guacamole/bin/initdb.sh --postgresql | \
	kubectl exec -i --context k3d-$(CLUSTER_NAME) --namespace $(NAMESPACE) deployment/$(RELEASE)-guacamole-postgres -- psql -U guacamole guacamole
	@echo "Guacamole database initialized sucessfully.";


dev:
	$(MAKE) -j5 dev-frontend dev-backend dev-oauth-mock dev-docs dev-storybook

dev-frontend:
	$(MAKE) -C frontend dev

dev-backend:
	$(MAKE) -C backend dev

dev-oauth-mock:
	$(MAKE) -C mocks/oauth start

dev-docs:
	$(MAKE) -C docs serve

dev-storybook:
	$(MAKE) -C frontend storybook

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
