# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

CLUSTER_NAME = collab-cluster
LOCAL_REGISTRY_NAME = localhost
CLUSTER_REGISTRY_NAME = myregistry.localhost
REGISTRY_PORT = 12345
RELEASE = dev-t4c-manager
NAMESPACE = t4c-manager
SESSION_NAMESPACE = t4c-sessions
EASE_DEBUG_PORT = 3390
PORT ?= 8080

# Adds support for msys
export MSYS_NO_PATHCONV := 1

build: backend frontend docs capella/remote readonly

build-all: build t4c-client importer

backend:
	python backend/generate_git_archival.py;
	docker build -t t4c/client/backend -t $(LOCAL_REGISTRY_NAME):$(REGISTRY_PORT)/capella/collab/backend backend
	docker push $(LOCAL_REGISTRY_NAME):$(REGISTRY_PORT)/capella/collab/backend

frontend:
	node frontend/fetch-version.ts
	docker build --build-arg CONFIGURATION=local -t t4c/client/frontend -t $(LOCAL_REGISTRY_NAME):$(REGISTRY_PORT)/capella/collab/frontend frontend
	docker push $(LOCAL_REGISTRY_NAME):$(REGISTRY_PORT)/capella/collab/frontend

capella:
	docker build -t base capella-dockerimages/base
	docker build -t capella/base capella-dockerimages/capella --build-arg BUILD_TYPE=online --build-arg CAPELLA_VERSION=5.2.0

importer:
	docker build -t t4c/client/importer -t $(LOCAL_REGISTRY_NAME):$(REGISTRY_PORT)/t4c/client/importer capella-dockerimages/importer
	docker push $(LOCAL_REGISTRY_NAME):$(REGISTRY_PORT)/t4c/client/importer

capella/remote: capella
	docker build -t capella/remote -t $(LOCAL_REGISTRY_NAME):$(REGISTRY_PORT)/t4c/client/remote/5.2:prod capella-dockerimages/remote
	docker push $(LOCAL_REGISTRY_NAME):$(REGISTRY_PORT)/t4c/client/remote/5.2:prod

docs:
	docker build -t capella/collab/docs -t $(LOCAL_REGISTRY_NAME):$(REGISTRY_PORT)/capella/collab/docs docs/user
	docker push $(LOCAL_REGISTRY_NAME):$(REGISTRY_PORT)/capella/collab/docs

t4c-client: capella
	docker build -t t4c/client/base capella-dockerimages/t4c
	docker build -t t4c/client/remote -t $(LOCAL_REGISTRY_NAME):$(REGISTRY_PORT)/t4c/client/remote --build-arg BASE_IMAGE=t4c/client/base capella-dockerimages/remote
	docker push $(LOCAL_REGISTRY_NAME):$(REGISTRY_PORT)/t4c/client/remote

readonly:
	docker build -t capella/ease --build-arg BASE_IMAGE=capella/base --build-arg BUILD_TYPE=online capella-dockerimages/ease
	docker build -t capella/ease/remote --build-arg BASE_IMAGE=capella/ease capella-dockerimages/remote
	docker build -t $(LOCAL_REGISTRY_NAME):$(REGISTRY_PORT)/capella/readonly -t $(LOCAL_REGISTRY_NAME):$(REGISTRY_PORT)/capella/readonly/5.2:prod --build-arg BASE_IMAGE=capella/ease/remote capella-dockerimages/readonly
	docker push $(LOCAL_REGISTRY_NAME):$(REGISTRY_PORT)/capella/readonly
	docker push $(LOCAL_REGISTRY_NAME):$(REGISTRY_PORT)/capella/readonly/5.2:prod

deploy: build helm-deploy open rollout

# Deploy with full T4C client support:
deploy-t4c: build-all helm-deploy open rollout

deploy-without-build: helm-deploy open rollout

helm-deploy:
	@k3d cluster list $(CLUSTER_NAME) >/dev/null || $(MAKE) create-cluster
	@kubectl create namespace t4c-sessions 2> /dev/null || true
	@helm upgrade --install \
		--kube-context k3d-$(CLUSTER_NAME) \
		--create-namespace \
		--namespace $(NAMESPACE) \
		--values helm/values.yaml \
		$$(test -f secrets.yaml && echo "--values secrets.yaml") \
		--set docker.registry.internal=k3d-$(CLUSTER_REGISTRY_NAME):$(REGISTRY_PORT) \
		--set mocks.oauth=True \
		--set target=local \
		--set general.port=8080 \
		--set backend.authentication.oauth.redirectURI="http://localhost:$(PORT)/oauth2/callback" \
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
	kubectl delete deployment -n t4c-manager $(RELEASE)-backend-postgres
	kubectl delete pvc -n t4c-manager $(RELEASE)-volume-backend-postgres
	$(MAKE) helm-deploy

rollout:
	kubectl --context k3d-$(CLUSTER_NAME) rollout restart deployment -n $(NAMESPACE) $(RELEASE)-backend
	kubectl --context k3d-$(CLUSTER_NAME) rollout restart deployment -n $(NAMESPACE) $(RELEASE)-frontend
	kubectl --context k3d-$(CLUSTER_NAME) rollout restart deployment -n $(NAMESPACE) $(RELEASE)-docs

undeploy:
	helm uninstall --kube-context k3d-$(CLUSTER_NAME) --namespace $(NAMESPACE) $(RELEASE)
	kubectl --context k3d-$(CLUSTER_NAME) delete --all deployments -n $(SESSION_NAMESPACE)

create-cluster:
	type k3d || { echo "K3D is not installed, install k3d and run 'make create-cluster' again"; exit 1; }
	k3d registry list $(CLUSTER_REGISTRY_NAME) 2>&- || k3d registry create $(CLUSTER_REGISTRY_NAME) --port $(REGISTRY_PORT)
	k3d cluster list $(CLUSTER_NAME) 2>&- || k3d cluster create $(CLUSTER_NAME) \
		--registry-use k3d-$(CLUSTER_REGISTRY_NAME):$(REGISTRY_PORT) \
		--port "8080:80@loadbalancer"
	kubectl cluster-info

delete-cluster:
	k3d cluster list $(CLUSTER_NAME) 2>&- && k3d cluster delete $(CLUSTER_NAME)

.ONESHELL:
wait:
	@echo "-----------------------------------------------------------"
	@echo "--- Please wait until all services are in running state ---"
	@echo "-----------------------------------------------------------"
	@(kubectl get --context k3d-$(CLUSTER_NAME) -n $(NAMESPACE) --watch pods) &
	@kubectl wait --context k3d-$(CLUSTER_NAME) -n $(NAMESPACE) --for=condition=Ready --all pods --timeout=5m
	@kill %%

.ONESHELL:
provision-guacamole:
	@echo "Waiting for guacamole container, before we can initialize the database..."
	@kubectl get -n $(NAMESPACE) --watch pods &
	@sleep 2
	@kubectl wait --for=condition=Ready pods --timeout=5m --context k3d-$(CLUSTER_NAME) -n $(NAMESPACE) -l id=$(RELEASE)-deployment-guacamole-guacamole
	@kubectl wait --for=condition=Ready pods --timeout=5m --context k3d-$(CLUSTER_NAME) -n $(NAMESPACE) -l id=$(RELEASE)-deployment-guacamole-postgres
	@kill %%
	@kubectl exec --context k3d-$(CLUSTER_NAME) --namespace $(NAMESPACE) $$(kubectl get pod --namespace $(NAMESPACE) -l id=$(RELEASE)-deployment-guacamole-guacamole --no-headers | cut -f1 -d' ') -- /opt/guacamole/bin/initdb.sh --postgres | \
	kubectl exec -ti --context k3d-$(CLUSTER_NAME) --namespace $(NAMESPACE) $$(kubectl get pod --namespace $(NAMESPACE) -l id=$(RELEASE)-deployment-guacamole-postgres --no-headers | cut -f1 -d' ') -- psql -U guacamole guacamole
	@echo "Guacamole database initialized sucessfully.";

# Execute with `make -j3 dev`
dev: dev-oauth-mock dev-frontend dev-backend

dev-frontend:
	$(MAKE) -C frontend dev

dev-backend:
	$(MAKE) -C backend dev

dev-oauth-mock:
	$(MAKE) -C mocks/oauth start

dev-cleanup:
	$(MAKE) -C backend cleanup

backend-logs:
	kubectl logs -f -n $(NAMESPACE) -l id=$(RELEASE)-deployment-backend

ns:
	kubectl config set-context k3d-$(CLUSTER_NAME) --namespace=$(NAMESPACE)

dashboard:
	kubectl apply --context k3d-$(CLUSTER_NAME) -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.5.0/aio/deploy/recommended.yaml
	kubectl apply -f dashboard/dashboard.rolebinding.yml -f dashboard/dashboard.serviceaccount.yml
	echo "Please open the portal: http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/#/login"
	echo "Please use the following token: $$(kubectl -n default create token dashboard-admin)"
	kubectl proxy

.PHONY: *
