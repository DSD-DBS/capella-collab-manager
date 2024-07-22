# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

start:
	export MSYS_NO_PATHCONV=1; \
	docker start oauth-mock || \
	docker run \
		--name oauth-mock \
		-v $$(pwd)/conf.json:/opt/conf.json \
		-p 8083:8080 \
		-e JSON_CONFIG_PATH=/opt/conf.json \
		ghcr.io/navikt/mock-oauth2-server:2.1.8

stop:
	docker stop oauth-mock && \
	docker rm oauth-mock
