# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

include .env
export

dev:
	docker build -t t4c/client/ease/remote --build-arg BASE_IMAGE=t4c/client/ease ../../capella-dockerimages/remote
	docker build -t t4c/client/ease/remote/debug --build-arg BASE_IMAGE=t4c/client/ease/remote ../../capella-dockerimages/ease/debug
	docker stop ease-debug || true
	docker rm ease-debug || true
	docker run -d \
		--name ease-debug \
		-p $(EASE_DEBUG_PORT):3389 \
		-v $(shell pwd)/local/scripts:/opt/scripts \
		-v $(shell pwd)/capella-dockerimages/ease/pyease:/opt/pyease \
		-e PYTHONPATH="/opt/pyease" \
		--env-file .env \
		t4c/client/ease/remote/debug
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

endpoint:
	kubectl get -n $(NAMESPACE) -o jsonpath="{.subsets[0].addresses[0].ip}" endpoints $(RELEASE)-ease

exec:
	kubectl exec --stdin --tty -n $(NAMESPACE) $(shell kubectl get -n debug -o jsonpath="{.items[0].metadata.name}" pods -l "id=$(RELEASE)-deployment-ease") -- /bin/bash

undeploy:
	helm uninstall \
		--kube-context $(CONTEXT) \
		--namespace $(NAMESPACE) \
		$(RELEASE)
