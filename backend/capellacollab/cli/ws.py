# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import typer
from kubernetes import client, config

app = typer.Typer()


@app.command()
def list(namespace: str = None):
    config.load_kube_config()
    core_api = client.CoreV1Api()

    for item in core_api.list_namespaced_persistent_volume_claim(
        namespace=namespace or get_current_namespace(), watch=False
    ).items:
        print(item.metadata.name)


@app.command()
def download(volume_name: str, namespace: str = None):
    config.load_kube_config()
    pod = create_temporary_pod(volume_name, namespace)
    print(pod)


def create_temporary_pod(volume_name: str, namespace: str):
    name = f"download-{volume_name}"

    containers = [
        client.V1Container(
            name=name,
            image="alpine:latest",
            command=["sleep", "infinity"],
            volume_mounts=[
                client.V1VolumeMount(
                    name=volume_name,
                    mount_path="/mnt",
                    read_only=True,
                )
            ],
            image_pull_policy="Always",
        )
    ]

    volumes = [
        client.V1Volume(
            name=volume_name,
            persistent_volume_claim=client.V1PersistentVolumeClaimVolumeSource(
                claim_name=volume_name
            ),
        )
    ]

    pod = client.V1Pod(
        kind="Pod",
        api_version="v1",
        metadata=client.V1ObjectMeta(name=name),
        spec=client.V1PodSpec(
            # security_context=pod_security_context,
            containers=containers,
            volumes=volumes,
            restart_policy="Never",
        ),
    )

    return client.CoreV1Api().create_namespaced_pod(namespace, pod)


def get_current_namespace():
    try:
        _, active_context = config.list_kube_config_contexts()
        return active_context["context"]["namespace"]
    except KeyError:
        return "default"
