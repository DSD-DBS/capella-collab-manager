# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

CLUSTER_NAME = collab-cluster

RELEASE = dev
NAMESPACE = collab-manager
SESSION_NAMESPACE = collab-sessions

K3D_REGISTRY_PORT = 12345
K3D_REGISTRY_NAME = myregistry.localhost

DOCKER_REGISTRY ?= k3d-$(K3D_REGISTRY_NAME):$(K3D_REGISTRY_PORT)/capella/collab
CAPELLACOLLAB_SESSIONS_REGISTRY ?= k3d-$(K3D_REGISTRY_NAME):$(K3D_REGISTRY_PORT)

DOCKER_TAG ?= $$(git describe --tags --abbrev=0)

CAPELLA_VERSION ?= 7.0.0

DEVELOPMENT_MODE ?= 0
DEPLOY_GUACAMOLE ?= 0

TIMEOUT ?= 10m

CAPELLA_DOCKERIMAGES = $(MAKE) -C capella-dockerimages PUSH_IMAGES=1 DOCKER_PREFIX=$(CAPELLACOLLAB_SESSIONS_REGISTRY)

# Adds support for msys
export MSYS_NO_PATHCONV := 1

# Use Docker Buildkit on Linux
export DOCKER_BUILDKIT=1

CREATE_ENV_FILE:=$(shell touch .env)
include .env

.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS = -euo pipefail -c

build: backend frontend docs guacamole session-preparation

backend:
	python backend/generate_git_archival.py;
	docker build -t $@ -t $(DOCKER_REGISTRY)/$@ -t $(DOCKER_REGISTRY)/$@:$(DOCKER_TAG) backend
	docker push $(DOCKER_REGISTRY)/$@
	docker push $(DOCKER_REGISTRY)/$@:$(DOCKER_TAG)

frontend:
	$(MAKE) -C frontend fetch-version
	docker build -t $@ -t $(DOCKER_REGISTRY)/$@ -t $(DOCKER_REGISTRY)/$@:$(DOCKER_TAG) frontend
	docker push $(DOCKER_REGISTRY)/$@
	docker push $(DOCKER_REGISTRY)/$@:$(DOCKER_TAG)

guacamole:
	docker build -t $@ -t $(DOCKER_REGISTRY)/$@ -t $(DOCKER_REGISTRY)/$@:$(DOCKER_TAG) images/guacamole
	docker push $(DOCKER_REGISTRY)/$@
	docker push $(DOCKER_REGISTRY)/$@:$(DOCKER_TAG)

session-preparation:
	docker build -t $@ -t $(DOCKER_REGISTRY)/$@ -t $(DOCKER_REGISTRY)/$@:$(DOCKER_TAG) images/session-preparation
	docker push $(DOCKER_REGISTRY)/$@
	docker push $(DOCKER_REGISTRY)/$@:$(DOCKER_TAG)

docs:
	docker build -t $@ -t $(DOCKER_REGISTRY)/$@ -t $(DOCKER_REGISTRY)/$@:$(DOCKER_TAG) docs
	docker push $(DOCKER_REGISTRY)/$@
	docker push $(DOCKER_REGISTRY)/$@:$(DOCKER_TAG)

trivy:
	COMMON_ARGS="--exit-code 0 --severity HIGH,CRITICAL --ignore-unfixed"
	trivy image $$COMMON_ARGS --ignorefile backend/.trivyignore $(DOCKER_REGISTRY)/backend:$(DOCKER_TAG)
	trivy image $$COMMON_ARGS --ignorefile frontend/.trivyignore $(DOCKER_REGISTRY)/frontend:$(DOCKER_TAG)
	trivy image $$COMMON_ARGS --ignorefile images/guacamole/.trivyignore $(DOCKER_REGISTRY)/guacamole:$(DOCKER_TAG)
	trivy image $$COMMON_ARGS --ignorefile images/session-preparation/.trivyignore $(DOCKER_REGISTRY)/session-preparation:$(DOCKER_TAG)
	trivy image $$COMMON_ARGS --ignorefile docs/.trivyignore $(DOCKER_REGISTRY)/docs:$(DOCKER_TAG)

base:
	$(CAPELLA_DOCKERIMAGES) \
		DOCKER_TAG="latest" \
		base

capella: base
	$(CAPELLA_DOCKERIMAGES) \
		DOCKER_TAG="$(CAPELLA_VERSION)-latest" \
		CAPELLA_VERSION="$(CAPELLA_VERSION)" \
		BASE_IMAGE_TAG="latest" \
		capella/remote -o base

t4c-client:
	$(CAPELLA_DOCKERIMAGES) \
		DOCKER_TAG="$(CAPELLA_VERSION)-latest" \
		CAPELLA_VERSION="$(CAPELLA_VERSION)" \
		BASE_IMAGE_TAG="latest" \
		t4c/client/remote -o base

jupyter: base
	$(CAPELLA_DOCKERIMAGES) \
		DOCKER_TAG="python-3.11-latest" \
		BASE_IMAGE_TAG="latest" \
		jupyter-notebook -o base

deploy: build jupyter capella helm-deploy rollout open

# Deploy with full T4C client support:
deploy-t4c: build jupyter t4c-client helm-deploy rollout open

deploy-without-build: helm-deploy rollout open

helm-deploy:
	@k3d cluster list $(CLUSTER_NAME) >/dev/null || $(MAKE) create-cluster
	@kubectl create namespace $(SESSION_NAMESPACE) 2> /dev/null || true
	@[[ ! $$(helm dependency list ./helm | sed '1d' | sed '/^$$/d' | grep -wv ok) ]] || helm dependency update ./helm;
	@echo "Start helm upgrade..."
	HELM_PACKAGE_DIR=$$(mktemp -d)
	helm package --app-version=$$(git rev-parse --abbrev-ref HEAD) --version=$$(git describe --tags) -d "$$HELM_PACKAGE_DIR" helm
	@helm upgrade --install \
		--kube-context k3d-$(CLUSTER_NAME) \
		--create-namespace \
		--namespace $(NAMESPACE) \
		--values helm/values.yaml \
		$$(test -f secrets.yaml && echo "--values secrets.yaml") \
		--set docker.registry.internal=$(DOCKER_REGISTRY) \
		--set docker.registry.sessions=$(CAPELLACOLLAB_SESSIONS_REGISTRY) \
		--set docker.tag=$(DOCKER_TAG) \
		--set mocks.oauth=True \
		--set mocks.smtp=True \
		--set backend.authentication.claimMapping.username=sub \
		--set backend.authentication.endpoints.authorization=https://localhost/default/authorize \
		--set development=$(DEVELOPMENT_MODE) \
		--set cluster.ingressClassName=traefik \
		--set cluster.ingressNamespace=kube-system \
		--set backend.k8sSessionNamespace="$(SESSION_NAMESPACE)" \
		--set loki.gateway.basicAuth.password="localLokiPassword" \
		--set grafana.adminPassword="admin" \
		--set database.backend.internal.password="secret" \
		--set database.guacamole.internal.password="secret" \
		--set valkey.password="secret" \
		--set replicaCount.frontend=1 \
		--set replicaCount.backend=1 \
		--set replicaCount.routing=1 \
		--set guacamole.enabled=$(DEPLOY_GUACAMOLE) \
		$(RELEASE) $$HELM_PACKAGE_DIR/collab-manager-*.tgz
	rm -rf "$$HELM_PACKAGE_DIR"
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
	DEPLOYMENTS="backend frontend docs"

	if [[ $(DEPLOY_GUACAMOLE) == 1 ]]; then
		DEPLOYMENTS+=" guacamole-guacamole";
	fi

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
	kubectl create namespace $(SESSION_NAMESPACE)

install-vpa:
	[ -d "autoscaler" ] || git clone https://github.com/kubernetes/autoscaler.git
	cd autoscaler/vertical-pod-autoscaler
	./hack/vpa-up.sh
	kubectl --namespace=kube-system get pods | grep vpa

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
	if [[ $(DEPLOY_GUACAMOLE) == 0 ]]; then
		echo "Guacamole is not deployed. Skipping initialization.";
		exit 0;
	fi
	echo "Waiting for guacamole container, before we can initialize the database..."
	@kubectl get --context k3d-$(CLUSTER_NAME) -n $(NAMESPACE) --watch pods &
	sleep 2
	@kubectl wait --for=condition=Ready pods --timeout=$(TIMEOUT) --context k3d-$(CLUSTER_NAME) -n $(NAMESPACE) -l id=$(RELEASE)-deployment-guacamole-guacamole
	@kubectl wait --for=condition=Ready pods --timeout=$(TIMEOUT) --context k3d-$(CLUSTER_NAME) -n $(NAMESPACE) -l id=$(RELEASE)-deployment-guacamole-postgres
	@kill %%
	TABLE_EXISTS=$$(kubectl exec --context k3d-$(CLUSTER_NAME) -n $(NAMESPACE) --container $(RELEASE)-guacamole-postgres deployment/$(RELEASE)-guacamole-postgres -- psql -U guacamole -tAc "SELECT EXISTS(SELECT 1 FROM information_schema .tables WHERE table_name='guacamole_user');")
	if [[ $$TABLE_EXISTS == "t" ]]; then
		echo "Guacamole database already initialized. Skipping initialization.";
		exit 0;
	fi
	@kubectl exec --context k3d-$(CLUSTER_NAME) --namespace $(NAMESPACE) --container $(RELEASE)-guacamole-guacamole deployment/$(RELEASE)-guacamole-guacamole -- /opt/guacamole/bin/initdb.sh --postgresql | \
	kubectl exec -i --context k3d-$(CLUSTER_NAME) --namespace $(NAMESPACE) deployment/$(RELEASE)-guacamole-postgres -- psql -U guacamole guacamole
	@echo "Guacamole database initialized successfully.";

reach-registry:
	@r=0;
	curl http://k3d-myregistry.localhost:12345/v2/ || r=$$?
	if [ $$r -ne 0 ]; then
		echo "The registry is not reachable. Possible solutions are described in our documentation: "
		echo "https://dsd-dbs.github.io/capella-collab-manager/development/troubleshooting/"
		exit 1
	fi

dev:
	$(MAKE) -j6 dev-frontend dev-backend dev-oauth-mock dev-smtp-mock dev-docs dev-storybook

dev-frontend:
	$(MAKE) -C frontend dev

dev-backend:
	$(MAKE) -C backend dev

dev-oauth-mock:
	$(MAKE) -C mocks/oauth start

dev-smtp-mock:
	$(MAKE) -C mocks/smtp start

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

synchronize-rsa-keys:
	export POD_NAME=$$(kubectl get pods \
		--context k3d-$(CLUSTER_NAME) \
		-n $(NAMESPACE) \
		-l id=$(RELEASE)-deployment-backend \
		-o jsonpath="{.items[0].metadata.name}")

	echo "Found Pod $$POD_NAME"

	kubectl exec \
		--context k3d-$(CLUSTER_NAME) \
		-n $(NAMESPACE) \
		--container $(RELEASE)-backend \
		$$POD_NAME \
		-- /opt/backend/.venv/bin/python -m capellacollab.cli keys export /tmp/private.key

	kubectl cp \
		--context k3d-$(CLUSTER_NAME) \
		-n $(NAMESPACE) \
		--container $(RELEASE)-backend \
		$$POD_NAME:/tmp/private.key \
		/tmp/private.key

	$(MAKE) -C backend import-rsa-key

	rm /tmp/private.key
	$(MAKE) -C backend trigger-reload;

openapi:
	$(MAKE) -C backend openapi
	$(MAKE) -C frontend openapi

.PHONY: *
