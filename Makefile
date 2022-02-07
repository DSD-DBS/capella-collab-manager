
CLUSTER_NAME = mycluster
REGISTRY_NAME = myregistry.localhost
REGISTRY_PORT = 12345
RELEASE = dev-t4c-manager
NAMESPACE = t4c-manager
SESSIONS_NAMESPACE = t4c-sessions

all: backend frontend

backend:
	docker build -t t4c/client/backend -t $(REGISTRY_NAME):$(REGISTRY_PORT)/t4c/client/backend backend
	docker push $(REGISTRY_NAME):$(REGISTRY_PORT)/t4c/client/backend

frontend:
	docker build -t t4c/client/frontend -t $(REGISTRY_NAME):$(REGISTRY_PORT)/t4c/client/frontend frontend
	docker push $(REGISTRY_NAME):$(REGISTRY_PORT)/t4c/client/frontend

#deploy: backend frontend
deploy:
	k3d cluster list $(CLUSTER_NAME) 2>&- || $(MAKE) create-cluster
	# it assumes that default namespace for sessions "t4c-sessions" is already there
	kubectl create namespace $(SESSIONS_NAMESPACE) --dry-run=client -o yaml | kubectl apply -f -
	helm upgrade --install \
		--kube-context k3d-$(CLUSTER_NAME) \
		--create-namespace \
	        --namespace $(NAMESPACE) \
		--values helm/options.yaml \
		--set docker.repository=k3d-$(REGISTRY_NAME):$(REGISTRY_PORT) \
		$(RELEASE) ./helm

undeploy:
	helm uninstall --kube-context k3d-$(CLUSTER_NAME) --namespace $(NAMESPACE) $(RELEASE)

create-cluster:
	type k3d || { echo "K3D is not installed, install k3d and run 'make create-cluster' again"; exit 1; }
	k3d registry list $(REGISTRY_NAME) 2>&- || k3d registry create $(REGISTRY_NAME) --port $(REGISTRY_PORT)
	k3d cluster list $(CLUSTER_NAME) 2>&- || k3d cluster create $(CLUSTER_NAME) --registry-use k3d-$(REGISTRY_NAME):$(REGISTRY_PORT)
	kubectl cluster-info

.PHONY: backend frontend deploy create-cluster
