# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

CLUSTER_NAME = collab-cluster
LOCAL_REGISTRY_NAME = localhost
CLUSTER_REGISTRY_NAME = myregistry.localhost
REGISTRY_PORT = 12345
RELEASE = dev-t4c-manager
NAMESPACE = t4c-manager
SESSION_NAMESPACE = t4c-sessions
EASE_DEBUG_PORT = 3390

all: backend frontend

build: backend frontend capella

build-all: build ease

backend:
	docker build -t t4c/client/backend -t $(LOCAL_REGISTRY_NAME):$(REGISTRY_PORT)/capella/collab/backend backend
	docker push $(LOCAL_REGISTRY_NAME):$(REGISTRY_PORT)/capella/collab/backend

frontend:
	docker build --build-arg CONFIGURATION=local -t t4c/client/frontend -t $(LOCAL_REGISTRY_NAME):$(REGISTRY_PORT)/capella/collab/frontend frontend
	docker push $(LOCAL_REGISTRY_NAME):$(REGISTRY_PORT)/capella/collab/frontend

capella: capella-download
	docker build -t base capella-dockerimages/base
	docker build -t capella/base capella-dockerimages/capella

capella/remote: capella
	docker build -t capella/remote -t $(LOCAL_REGISTRY_NAME):$(REGISTRY_PORT)/t4c/client/remote capella-dockerimages/remote
	docker push $(LOCAL_REGISTRY_NAME):$(REGISTRY_PORT)/t4c/client/remote

capella-download:
	cd capella-dockerimages/capella/archives; \
	if [ -f "capella.tar.gz" ] || [ -f "capella.zip" ]; \
	then \
		echo "Found existing capella archive."; \
	else \
		curl -L --output capella.tar.gz 'https://ftp.acc.umu.se/mirror/eclipse.org/capella/core/products/releases/5.2.0-R20211130-125709/capella-5.2.0.202111301257-linux-gtk-x86_64.tar.gz'; \
	fi

t4c-client: capella
	docker build -t t4c/client/base capella-dockerimages/t4c
	docker build -t t4c/client/remote -t $(LOCAL_REGISTRY_NAME):$(REGISTRY_PORT)/t4c/client/remote --build-arg BASE_IMAGE=t4c/client/base capella-dockerimages/remote
	docker push $(LOCAL_REGISTRY_NAME):$(REGISTRY_PORT)/t4c/client/remote

readonly:
	docker build -t capella/ease --build-arg BASE_IMAGE=capella/base --build-arg BUILD_TYPE=online capella-dockerimages/ease
	docker build -t capella/ease/remote --build-arg BASE_IMAGE=capella/ease capella-dockerimages/remote
	docker build -t $(LOCAL_REGISTRY_NAME):$(REGISTRY_PORT)/capella/readonly --build-arg BASE_IMAGE=capella/ease/remote capella-dockerimages/readonly
	docker push $(LOCAL_REGISTRY_NAME):$(REGISTRY_PORT)/capella/readonly

ease:
	docker build -t $(LOCAL_REGISTRY_NAME):$(REGISTRY_PORT)/t4c/client/ease --build-arg BASE_IMAGE=t4c/client/base --build-arg BUILD_TYPE=online capella-dockerimages/ease
	docker push $(LOCAL_REGISTRY_NAME):$(REGISTRY_PORT)/t4c/client/ease

mock:
	docker build -t t4c/server/mock -t $(LOCAL_REGISTRY_NAME):$(REGISTRY_PORT)/t4c/server/mock mocks/t4c-server
	docker push $(LOCAL_REGISTRY_NAME):$(REGISTRY_PORT)/t4c/server/mock

	docker build -t t4c/licence/mock -t $(LOCAL_REGISTRY_NAME):$(REGISTRY_PORT)/t4c/licence/mock mocks/licence-server
	docker push $(LOCAL_REGISTRY_NAME):$(REGISTRY_PORT)/t4c/licence/mock

capella-dockerimages: capella t4c-client readonly ease

deploy: backend frontend capella/remote mock helm-deploy open rollout

# Deploy with full T4C support:
deploy-t4c: backend frontend capella t4c-client readonly ease mock helm-deploy open rollout

helm-deploy:
	k3d cluster list $(CLUSTER_NAME) 2>&- || $(MAKE) create-cluster
	kubectl create namespace t4c-sessions || true
	helm upgrade --install \
		--kube-context k3d-$(CLUSTER_NAME) \
		--create-namespace \
		--namespace $(NAMESPACE) \
		--values helm/values.yaml \
		$$(test -f secrets.yaml && echo "--values secrets.yaml") \
		--set docker.registry.internal=k3d-$(CLUSTER_REGISTRY_NAME):$(REGISTRY_PORT) \
		--set general.port=8080 \
		--set t4cServer.apis.usageStats="http://$(RELEASE)-licence-server-mock:80/mock" \
		--set t4cServer.apis.restAPI="http://$(RELEASE)-t4c-server-mock:80/mock/api/v1.0" \
		--wait --timeout 10m \
		--debug \
		$(RELEASE) ./helm
	$(MAKE) .provision-guacamole .provision-backend

open:
	export URL=http://localhost:8080; \
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

rollout: backend frontend
	kubectl --context k3d-$(CLUSTER_NAME) rollout restart deployment -n $(NAMESPACE) $(RELEASE)-backend
	kubectl --context k3d-$(CLUSTER_NAME) rollout restart deployment -n $(NAMESPACE) $(RELEASE)-frontend

undeploy:
	helm uninstall --kube-context k3d-$(CLUSTER_NAME) --namespace $(NAMESPACE) $(RELEASE)
	kubectl --context k3d-$(CLUSTER_NAME) delete --all deployments -n $(SESSION_NAMESPACE)
	rm -f .provision-guacamole .provision-backend

create-cluster:
	type k3d || { echo "K3D is not installed, install k3d and run 'make create-cluster' again"; exit 1; }
	k3d registry list $(CLUSTER_REGISTRY_NAME) 2>&- || k3d registry create $(CLUSTER_REGISTRY_NAME) --port $(REGISTRY_PORT)
	k3d cluster list $(CLUSTER_NAME) 2>&- || k3d cluster create $(CLUSTER_NAME) \
		--registry-use k3d-$(CLUSTER_REGISTRY_NAME):$(REGISTRY_PORT) \
		--port "8080:80@loadbalancer"
	kubectl cluster-info

delete-cluster:
	k3d cluster list $(CLUSTER_NAME) 2>&- && k3d cluster delete $(CLUSTER_NAME)
	rm -f .provision-guacamole .provision-backend

.provision-guacamole:
	export MSYS_NO_PATHCONV=1; \
	kubectl exec --context k3d-$(CLUSTER_NAME) --namespace $(NAMESPACE) $$(kubectl get pod --context k3d-$(CLUSTER_NAME) --namespace $(NAMESPACE) -l id=$(RELEASE)-deployment-guacamole-guacamole --no-headers | cut -f1 -d' ') -- /opt/guacamole/bin/initdb.sh --postgres | \
	kubectl exec -ti --context k3d-$(CLUSTER_NAME) --namespace $(NAMESPACE) $$(kubectl get pod --context k3d-$(CLUSTER_NAME) --namespace $(NAMESPACE) -l id=$(RELEASE)-deployment-guacamole-postgres --no-headers | cut -f1 -d' ') -- psql -U guacamole guacamole && \
	touch .provision-guacamole

.provision-backend:
	echo "insert into repository_user_association values ('$(MY_EMAIL)', 'default', 'WRITE', 'MANAGER');" | kubectl exec --context k3d-$(CLUSTER_NAME) --namespace $(NAMESPACE) $$(kubectl get pod --context k3d-$(CLUSTER_NAME) --namespace $(NAMESPACE) -l id=$(RELEASE)-deployment-backend-postgres --no-headers | cut -f1 -d' ') -- psql -U backend backend && \
	touch .provision-backend

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

.PHONY: *
