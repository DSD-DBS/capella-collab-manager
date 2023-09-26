# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import contextlib
import select
import sys
import time
import uuid
from pathlib import Path

import typer
from kubernetes import client, config, stream
from websocket import ABNF

app = typer.Typer()

mount_path = "/workspace"


@app.command()
def volumes(namespace: str = None):
    config.load_kube_config()
    core_api = client.CoreV1Api()

    for item in core_api.list_namespaced_persistent_volume_claim(
        namespace=namespace or get_current_namespace(), watch=False
    ).items:
        print(item.metadata.name)


@app.command()
def ls(volume_name: str, path: str = "/workspace", namespace: str = None):
    config.load_kube_config()
    v1 = client.CoreV1Api()

    with pod_for_volume(volume_name, namespace, mount_path, v1) as pod_name:
        for data in stream_tar_from_pod(pod_name, namespace, ["ls", path], v1):
            sys.stdout.write(data.decode("utf-8", "replace"))


@app.command()
def backup(volume_name: str, namespace: str = None, out: Path = None):
    config.load_kube_config()
    v1 = client.CoreV1Api()
    if not out:
        out = Path.cwd()

    targz = out / f"{volume_name}.tar.gz"

    with pod_for_volume(volume_name, namespace, mount_path, v1) as pod_name:
        print(f"Downloading workspace volume to '{targz}'")

        with targz.open("wb") as outfile:
            for data in stream_tar_from_pod(
                pod_name, namespace, ["tar", "zcf", "-", mount_path], v1
            ):
                outfile.write(data)


@contextlib.contextmanager
def pod_for_volume(
    volume_name: str, namespace: str, mount_path: str, v1: client.CoreV1Api
):
    name = f"ws-download-{volume_name}-{uuid.uuid1()}"[:63]

    containers = [
        client.V1Container(
            name=name,
            image="alpine:latest",
            command=["sleep", "infinity"],
            volume_mounts=[
                client.V1VolumeMount(
                    name="vol",
                    mount_path=mount_path,
                    read_only=True,
                )
            ],
            image_pull_policy="Always",
        )
    ]

    volumes = [
        client.V1Volume(
            name="vol",
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
            containers=containers,
            volumes=volumes,
            restart_policy="Never",
        ),
    )

    v1.create_namespaced_pod(namespace, pod)

    while not is_pod_ready(name, namespace, v1):
        print("Waiting for pod to come online...")
        time.sleep(2)

    yield name

    v1.delete_namespaced_pod(name, namespace)


def get_current_namespace():
    try:
        _, active_context = config.list_kube_config_contexts()
        return active_context["context"]["namespace"]
    except KeyError:
        return "default"


def is_pod_ready(pod_name, namespace, v1):
    try:
        pod_status = v1.read_namespaced_pod_status(pod_name, namespace)
        return pod_status.status.phase == "Running"
    except client.exceptions.ApiException as e:
        print(
            f"Exception when calling CoreV1Api->read_namespaced_pod_status: {e}"
        )
        return False


def stream_tar_from_pod(pod_name, namespace, command, v1):
    exec_stream = stream.stream(
        v1.connect_get_namespaced_pod_exec,
        pod_name,
        namespace,
        command=command,
        stderr=True,
        stdin=True,
        stdout=True,
        tty=False,
        _preload_content=False,
    )

    try:
        reader = WSFileManager(exec_stream)
        while True:
            out, err, closed = reader.read_bytes()
            if out:
                yield out
            elif err:
                print(err.decode("utf-8", "replace"))
            if closed:
                break
    finally:
        exec_stream.close()


class WSFileManager:
    """WS wrapper to manage read and write bytes in K8s WSClient."""

    def __init__(self, ws_client):
        self.ws_client = ws_client

    def read_bytes(self, timeout=0) -> bytes:
        stdout_bytes = None
        stderr_bytes = None

        if not self.ws_client.is_open():
            return stdout_bytes, stderr_bytes, not self.ws_client._connected

        if not self.ws_client.sock.connected:
            self.ws_client._connected = False
            return stdout_bytes, stderr_bytes, not self.ws_client._connected

        r, _, _ = select.select((self.ws_client.sock.sock,), (), (), timeout)
        if not r:
            return stdout_bytes, stderr_bytes, not self.ws_client._connected

        op_code, frame = self.ws_client.sock.recv_data_frame(True)
        if op_code == ABNF.OPCODE_CLOSE:
            self.ws_client._connected = False
        elif op_code in (ABNF.OPCODE_BINARY, ABNF.OPCODE_TEXT):
            data = frame.data
            if len(data) > 1:
                channel = data[0]
                data = data[1:]
                if data:
                    if channel == stream.ws_client.STDOUT_CHANNEL:
                        stdout_bytes = data
                    elif channel == stream.ws_client.STDERR_CHANNEL:
                        stderr_bytes = data
        return stdout_bytes, stderr_bytes, not self.ws_client._connected
