# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

start:
	docker run --rm \
		--name capella-collab-smtp-mock \
		-p 5000:80 \
		-p 587:25 \
		--env ServerOptions__TlsMode="StartTls" \
		rnwood/smtp4dev
