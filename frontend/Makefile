# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

export NG_FORCE_TTY=false

HOST ?= localhost

.ONESHELL:

dev: fetch-version
	pnpm run dev --open

types:
	npx tsc --noEmit --watch

fetch-version:
	python fetch-version.py

storybook:
	pnpm run storybook

build-storybook:
	pnpm run build-storybook

snapshots:
	rm -rf __screenshots__
	pnpx storycap http://localhost:6006 --serverCmd "pnpm run storybook" --flat

openapi:
	OPENAPI_DIR=$$(mktemp -d)
	docker run --rm --pull=always \
  		-v /tmp/openapi.json:/tmp/openapi.json \
		-v $$(pwd)/openapi_templates:/tmp/openapi_templates \
		-v $$OPENAPI_DIR:/tmp/output \
		-u $$(id -u $${USER}):$$(id -g $${USER}) \
		openapitools/openapi-generator-cli:v7.11.0 generate \
			-i /tmp/openapi.json \
			-t /tmp/openapi_templates \
			--global-property models,apis,supportingFiles="index.ts:api.ts:models.ts:variables.ts:configuration.ts:api.module.ts:param.ts:encoder.ts" \
			--additional-properties=fileNaming=kebab-case,legacyDiscriminatorBehavior=false \
			-g typescript-angular \
			-o /tmp/output
	cp ../LICENSES/.license_header_cc0.txt $$OPENAPI_DIR/.openapi-generator/FILES.license
	cp ../LICENSES/.license_header_cc0.txt $$OPENAPI_DIR/.openapi-generator/VERSION.license
	rsync -avh --delete $$OPENAPI_DIR/ $$(pwd)/src/app/openapi
	rm -rf $$OPENAPI_DIR
