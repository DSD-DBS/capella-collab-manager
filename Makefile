
CLUSTER_NAME = mycluster
REGISTRY_NAME = myregistry.localhost
REGISTRY_PORT = 12345
RELEASE = dev-t4c-manager
NAMESPACE = t4c-manager
SESSIONS_NAMESPACE = t4c-sessions
MY_EMAIL := amolenaar@xebia.com

all: backend frontend

backend:
	docker build -t t4c/client/backend -t $(REGISTRY_NAME):$(REGISTRY_PORT)/t4c/client/backend backend
	docker push $(REGISTRY_NAME):$(REGISTRY_PORT)/t4c/client/backend

frontend:
	docker build -t t4c/client/frontend -t $(REGISTRY_NAME):$(REGISTRY_PORT)/t4c/client/frontend frontend
	docker push $(REGISTRY_NAME):$(REGISTRY_PORT)/t4c/client/frontend

capella:
	docker build -t base capella-dockerimages/base
	docker build -t capella/base capella-dockerimages/capella
	docker build -t capella/remote -t $(REGISTRY_NAME):$(REGISTRY_PORT)/t4c/client/remote capella-dockerimages/remote
	docker push $(REGISTRY_NAME):$(REGISTRY_PORT)/t4c/client/remote

deploy: backend frontend capella
	k3d cluster list $(CLUSTER_NAME) 2>&- || $(MAKE) create-cluster
	# it assumes that default namespace for sessions "t4c-sessions" is already there
	kubectl create namespace $(SESSIONS_NAMESPACE) --dry-run=client -o yaml | kubectl apply -f -
	helm upgrade --install \
		--kube-context k3d-$(CLUSTER_NAME) \
		--create-namespace \
		--namespace $(NAMESPACE) \
		--values helm/values.yaml \
		$$(test -f secrets.yaml && echo "--values secrets.yaml") \
		--set docker.registry=k3d-$(REGISTRY_NAME):$(REGISTRY_PORT) \
		--set backend.initialAdmin=$(MY_EMAIL) \
		--wait --timeout 2m \
		$(RELEASE) ./helm
	$(MAKE) .provision-guacamole .provision-backend

rollout: backend frontend
	kubectl rollout restart deployment -n $(NAMESPACE) $(RELEASE)-backend
	kubectl rollout restart deployment -n $(NAMESPACE) $(RELEASE)-frontend

undeploy:
	helm uninstall --kube-context k3d-$(CLUSTER_NAME) --namespace $(NAMESPACE) $(RELEASE)
	rm -f .provision-guacamole .provision-backend

create-cluster:
	type k3d || { echo "K3D is not installed, install k3d and run 'make create-cluster' again"; exit 1; }
	k3d registry list $(REGISTRY_NAME) 2>&- || k3d registry create $(REGISTRY_NAME) --port $(REGISTRY_PORT)
	k3d cluster list $(CLUSTER_NAME) 2>&- || k3d cluster create $(CLUSTER_NAME) \
		--registry-use k3d-$(REGISTRY_NAME):$(REGISTRY_PORT) \
		--port "8081:80@loadbalancer"
	kubectl cluster-info

delete-cluster:
	k3d cluster list $(CLUSTER_NAME) 2>&- && k3d cluster delete $(CLUSTER_NAME)
	rm -f .provision-guacamole .provision-backend

.provision-guacamole:
	kubectl exec --namespace $(NAMESPACE) $$(kubectl get pod --namespace $(NAMESPACE) -l id=$(RELEASE)-deployment-guacamole-guacamole --no-headers | cut -f1 -d' ') -- /opt/guacamole/bin/initdb.sh --postgres | \
	kubectl exec -ti --namespace $(NAMESPACE) $$(kubectl get pod --namespace $(NAMESPACE) -l id=$(RELEASE)-deployment-guacamole-postgres --no-headers | cut -f1 -d' ') -- psql -U guacamole guacamole && \
	touch .provision-guacamole

.provision-backend:
	echo "insert into repository_user_association values ('$(MY_EMAIL)', 'default', 'WRITE', 'MANAGER');" | kubectl exec -ti --namespace $(NAMESPACE) $$(kubectl get pod --namespace $(NAMESPACE) -l id=$(RELEASE)-deployment-backend-postgres --no-headers | cut -f1 -d' ') -- psql -U backend backend && \
	touch .provision-backend

.PHONY: backend frontend capella deploy undeploy create-cluster delete-cluster persistent-volume
