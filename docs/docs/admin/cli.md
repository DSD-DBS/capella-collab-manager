<!--
 ~ SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

The Collaboration Manager repository contains a few tools that may come in
handy when you're an administrator of a Collaboration Manager setup.

The CLI (Command Line Interface) tool allows you to back up and restore user's
workspaces.

For the tools to work you'll need access to the Kubernetes cluster the
Collaboration manager is running on. In particular the namespace used to spawn
sessions.

## Installation

In order to use the CLI tooling, you'll need to have a local copy of the
collab-manager application and Python 3.11 installed.

```bash
git clone https://github.com/DSD-DBS/capella-collab-manager.git
cd capella-collab-manager/backend
python -m venv .venv
source .venv/bin/activate
pip install .
```

## Usage

Once your environment is set up, you can use the CLI tooling. The tooling is
located in a module:

```bash
python -m capellacollab.cli --help
```

This gives you the help information. The CLI tool currently has a subcommand:
`ws`, short for workspace.

```
Usage: python -m capellacollab.cli [OPTIONS] COMMAND [ARGS]...

Options:
  --install-completion [bash|zsh|fish|powershell|pwsh]
                                  Install completion for the specified shell.
  --show-completion [bash|zsh|fish|powershell|pwsh]
                                  Show completion for the specified shell, to
                                  copy it or customize the installation.
  --help                          Show this message and exit.

Commands:
  ws
```

You can discover the CLI on your own by printing the help messages of the
subcommands

```bash
python -m capellacollab.cli ws --help
python -m capellacollab.cli ws backup --help
```
