# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import contextlib
import pathlib
import select
import sys
import time
import typing as t
import uuid

import typer
import websocket  # type: ignore[import]
from kubernetes import client, config, stream

app = typer.Typer()

MOUNT_PATH = "/workspace"


@app.callback()
def init_kube():
    config.load_kube_config()


def get_current_namespace():
    try:
        _, active_context = config.list_kube_config_contexts()
        return active_context["context"]["namespace"]
    except KeyError:
        return "default"


NamespaceOption = typer.Option(
    "--namespace",
    "-n",
    help="Kubernetes namespace",
    default_factory=get_current_namespace,
)


@app.command()
def volumes(namespace: t.Annotated[str, NamespaceOption]):
    """List all Persistent Volume Claims in a kubernetes namespace."""
    core_api = client.CoreV1Api()

    for item in core_api.list_namespaced_persistent_volume_claim(
        namespace=namespace, watch=False
    ).items:
        print(item.metadata.name)


@app.command()
def ls(
    volume_name: str,
    namespace: t.Annotated[str, NamespaceOption],
    path: str = MOUNT_PATH,
):
    """List all files on a path in a Kubernetes Persistent Volume."""
    v1 = client.CoreV1Api()

    with pod_for_volume(volume_name, namespace, MOUNT_PATH, v1) as pod_name:
        for data in stream_tar_from_pod(pod_name, namespace, ["ls", path], v1):
            sys.stdout.write(data.decode("utf-8", "replace"))


@app.command()
def backup(
    volume_name: str,
    namespace: t.Annotated[str, NamespaceOption],
    out: pathlib.Path = pathlib.Path.cwd(),
):
    """Create a backup of all content in a Kubernetes Persistent Volume."""
    v1 = client.CoreV1Api()
    targz = out / f"{volume_name}.tar.gz"

    with pod_for_volume(volume_name, namespace, MOUNT_PATH, v1) as pod_name:
        print(f"Downloading workspace volume to '{targz}'")

        with targz.open("wb") as outfile:
            for data in stream_tar_from_pod(
                pod_name, namespace, ["tar", "zcf", "-", MOUNT_PATH], v1
            ):
                outfile.write(data)


@app.command()
def restore(
    volume_name: str,
    tarfile: t.Annotated[pathlib.Path, typer.Argument(exists=True)],
    namespace: t.Annotated[str, NamespaceOption],
    access_mode: str = "ReadWriteMany",
    storage_class_name: str = "persistent-sessions-csi",
    user_id: str | None = None,
):
    """Restore a backup to a Kubernetes Persistent Volume.

    If the volume does not exist, it is created. Note that
    `access-mode` and `storage-class-name` should match settings
    for your cluster.

    Optionally a `user-id` can be provided. All files then be owned
    by this user id.
    """
    v1 = client.CoreV1Api()

    create_persistent_volume(
        volume_name, namespace, access_mode, storage_class_name, v1
    )

    with pod_for_volume(
        volume_name, namespace, MOUNT_PATH, v1, read_only=False
    ) as pod_name:
        print(f"Restoring workspace volume to '{volume_name}'")

        with tarfile.open("rb") as infile:
            stream_tar_to_pod(pod_name, namespace, infile, v1)

        adjust_directory_permissions(
            pod_name,
            namespace,
            v1,
            user_id,
        )


@contextlib.contextmanager
def pod_for_volume(
    volume_name: str,
    namespace: str,
    mount_path: str,
    v1: client.CoreV1Api,
    read_only=True,
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
                    read_only=read_only,
                )
            ],
            image_pull_policy="Always",
        )
    ]

    volumes_ = [
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
            volumes=volumes_,
            restart_policy="Never",
        ),
    )

    v1.create_namespaced_pod(namespace, pod)

    while not is_pod_ready(name, namespace, v1):
        print("Waiting for pod to come online...")
        time.sleep(2)

    yield name

    v1.delete_namespaced_pod(name, namespace)


def create_persistent_volume(
    name: str, namespace: str, access_mode: str, storage_class_name: str, v1
):
    """Rebuild a PVC, according to the config defined in
    `capellacollab/sessions/hooks/persistent_workspace.py`.
    """

    prefix = "persistent-session-"
    username = name[len(prefix) :] if name.startswith(prefix) else name

    pvc = client.V1PersistentVolumeClaim(
        kind="PersistentVolumeClaim",
        api_version="v1",
        metadata=client.V1ObjectMeta(
            name=name,
            labels={
                "capellacollab/username": username,
            },
        ),
        spec=client.V1PersistentVolumeClaimSpec(
            access_modes=[access_mode],
            storage_class_name=storage_class_name,
            resources=client.V1ResourceRequirements(
                requests={"storage": "20Gi"}
            ),
        ),
    )

    try:
        v1.create_namespaced_persistent_volume_claim(namespace, pvc)
    except client.exceptions.ApiException as e:
        # Persistent volume already exists
        if e.status == 409:
            print(f"Using existing volume {name}")
            return
        raise


def adjust_directory_permissions(
    pod_name: str,
    namespace: str,
    v1: client.CoreV1Api,
    user_id: str | None,
    directory: str = MOUNT_PATH,
):
    resp = stream.stream(
        v1.connect_get_namespaced_pod_exec,
        pod_name,
        namespace,
        command=[
            "chown",
            "-R",
            f"{user_id}",
            directory,
        ],
        stderr=True,
        stdin=False,
        stdout=True,
        tty=False,
        _preload_content=False,
    )

    # Output the result
    while resp.is_open():
        resp.update(timeout=1)
        if resp.peek_stdout():
            print(f"STDOUT: {resp.read_stdout()}")
        if resp.peek_stderr():
            print(f"STDERR: {resp.read_stderr()}")


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


def stream_tar_to_pod(pod_name, namespace, infile, v1):
    exec_stream = stream.stream(
        v1.connect_get_namespaced_pod_exec,
        pod_name,
        namespace,
        command=["tar", "zxf", "-", "-C", "/"],
        # command=["cat"],
        stderr=True,
        stdin=True,
        stdout=True,
        tty=False,
        _preload_content=False,
    )

    try:
        while data := infile.read(4096):
            exec_stream.write_stdin(data)
            exec_stream.update(timeout=5)
            if exec_stream.peek_stdout():
                print("STDOUT: %s", exec_stream.read_stdout())
            if exec_stream.peek_stderr():
                print("STDERR: %s", exec_stream.read_stderr())
    finally:
        exec_stream.close()


class WSFileManager:
    """WS wrapper to manage read and write bytes in K8s WSClient."""

    def __init__(self, ws_client):
        self.ws_client = ws_client

    def read_bytes(self, timeout=0) -> tuple[bytes | None, bytes | None, bool]:
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
        if op_code == websocket.ABNF.OPCODE_CLOSE:
            self.ws_client._connected = False
        elif op_code in (
            websocket.ABNF.OPCODE_BINARY,
            websocket.ABNF.OPCODE_TEXT,
        ):
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
