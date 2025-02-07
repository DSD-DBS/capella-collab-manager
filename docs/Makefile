# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

install:
	uv venv $(VENV) --python 3.12
	uv pip install -r requirements.txt --python .venv/bin/python

serve:
	.venv/bin/mkdocs serve

build:
	.venv/bin/mkdocs build --strict
