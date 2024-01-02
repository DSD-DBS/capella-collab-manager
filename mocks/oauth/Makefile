# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

CERTS_DIR = ../../certs/

ssl:
	export MSYS_NO_PATHCONV=1; \
	openssl req -x509 -out $(CERTS_DIR)localhost.crt -keyout $(CERTS_DIR)localhost.key \
	-newkey rsa:2048 -nodes -sha256 \
	-subj '/CN=localhost' \
	-addext "subjectAltName = DNS:localhost";
	openssl pkcs12 -export -in $(CERTS_DIR)localhost.crt -inkey $(CERTS_DIR)localhost.key -out $(CERTS_DIR)localhost.p12 -passout "pass:"

start:
	export MSYS_NO_PATHCONV=1; \
	docker start oauth-mock || \
	docker run \
		--name oauth-mock \
		-v $$(pwd)/$(CERTS_DIR)localhost.p12:/opt/localhost.p12 \
		-v $$(pwd)/conf.json:/opt/conf.json \
		-p 8083:8080 \
		-e JSON_CONFIG_PATH=/opt/conf.json \
		ghcr.io/navikt/mock-oauth2-server:0.5.8

stop:
	docker stop oauth-mock && \
	docker rm oauth-mock
