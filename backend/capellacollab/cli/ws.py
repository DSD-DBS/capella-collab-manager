# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

# pylint: disable=bad-builtin

from __future__ import annotations

import contextlib
import datetime
import enum
import logging
import pathlib
import select
import sys
import time
import typing as t

import typer
import websocket
from rich import console, pretty, table

app = typer.Typer(
    help=(
        "List, backup and restore persistent workspaces. \n\n"
        "Before invoking the command, make sure that you have valid kubeconfig that points to the correct context."
    )
)

MOUNT_PATH = "/workspace"
PERSISTENT_SESSION_PREFIX = "persistent-session-"

LOGGER = logging.getLogger(__name__)


def init_kube():
    from kubernetes import config

    LOGGER.info("Loading kubectl configuration...")
    config.load_kube_config()
    LOGGER.info("Successfully loaded kubectl configuration.")


def get_current_namespace():
    from kubernetes import config

    try:
        _, active_context = config.list_kube_config_contexts()
        namespace = active_context["context"]["namespace"]
        LOGGER.info("Using namespace %s", namespace)
        return namespace
    except KeyError:
        return "default"


class LogLevel(str, enum.Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


LogLevelOption = typer.Option(
    "--log-level",
    "-l",
    help="Set the log level",
)

NamespaceOption = typer.Option(
    "--namespace",
    "-n",
    help="Kubernetes namespace",
    default_factory=get_current_namespace,
)

QuietOption = typer.Option("--quiet", "-q", help="Only display PVC names.")


@app.command()
def volumes(
    namespace: t.Annotated[str, NamespaceOption],
    log_level: t.Annotated[LogLevel, LogLevelOption] = LogLevel.INFO,
    quiet: t.Annotated[bool, QuietOption] = False,
):
    """List all volumes in a kubernetes namespace."""
    from kubernetes import client

    init_kube()
    core_api = client.CoreV1Api()

    logging.getLogger("kubernetes").setLevel(log_level.value)

    LOGGER.info("Listing all volumes in namespace %s", namespace)
    pvcs: list[client.V1PersistentVolumeClaim] = (
        core_api.list_namespaced_persistent_volume_claim(
            namespace=namespace, watch=False
        ).items
    )

    if quiet:
        for item in pvcs:
            print(item.metadata.name)
        return

    tbl = table.Table(
        table.Column("Name of the PVC", no_wrap=True),
        "Type",
        "Annotations",
        "Capacity",
        "Storage class",
        "Access Modes",
        "Age",
    )

    for item in pvcs:
        pvc_name: str = item.metadata.name
        annotations = {}
        volume_type = "Other"
        capacity = item.spec.resources.requests.get("storage", "-")
        storage_class = item.spec.storage_class_name
        access_modes = ", ".join(item.spec.access_modes)
        age: datetime.datetime = item.metadata.creation_timestamp

        if pvc_name.startswith(PERSISTENT_SESSION_PREFIX):
            annotations = {
                "capellacollab/username": pvc_name.removeprefix(
                    PERSISTENT_SESSION_PREFIX
                ),
            }
            volume_type = "Persistent user workspace"
        elif pvc_name.startswith("shared-workspace-"):
            annotations = {
                "capellacollab/project_slug": item.metadata.labels.get(
                    "capellacollab/project_slug"
                ),
            }
            volume_type = "Project-level file-share"

        tbl.add_row(
            pvc_name,
            volume_type,
            pretty.Pretty(annotations),
            capacity,
            storage_class,
            access_modes,
            str(datetime.datetime.now(datetime.UTC) - age),
        )

    console.Console().print(tbl)


@app.command()
def ls(
    volume_name: str,
    namespace: t.Annotated[str, NamespaceOption],
    path: str = MOUNT_PATH,
):
    """List all files on a path in a Kubernetes Persistent Volume."""

    init_kube()

    with pod_for_volume(volume_name, namespace) as pod_name:
        for data in stream_tar_from_pod(pod_name, namespace, ["ls", path]):
            sys.stdout.write(data.decode("utf-8", "replace"))


@app.command()
def backup(
    volume_name: str,
    namespace: t.Annotated[str, NamespaceOption],
    out: pathlib.Path = pathlib.Path.cwd(),
):
    """Create a backup of all content in a Kubernetes Persistent Volume."""
    init_kube()

    targz = out / f"{volume_name}.tar.gz"

    with pod_for_volume(volume_name, namespace) as pod_name:
        print(f"Downloading workspace volume to '{targz}'")

        with targz.open("wb") as outfile:
            for data in stream_tar_from_pod(
                pod_name, namespace, ["tar", "zcf", "-", MOUNT_PATH]
            ):
                outfile.write(data)


@app.command()
def restore(
    volume_name: str,
    tarfile: t.Annotated[pathlib.Path, typer.Argument(exists=True)],
    namespace: t.Annotated[str, NamespaceOption],
    access_mode: str = "ReadWriteMany",
    storage_class_name: str = "persistent-sessions-csi",
    user_id: t.Union[str, None] = None,
):
    """Restore a backup to a Kubernetes Persistent Volume.

    If the volume does not exist, it is created. Note that
    `access-mode` and `storage-class-name` should match settings
    for your cluster.

    Optionally a `user-id` can be provided. All files then be owned
    by this user id.
    """

    init_kube()

    create_persistent_volume(
        volume_name, namespace, access_mode, storage_class_name
    )

    with pod_for_volume(volume_name, namespace, read_only=False) as pod_name:
        print(f"Restoring workspace volume to '{volume_name}'")

        with tarfile.open("rb") as infile:
            stream_tar_to_pod(pod_name, namespace, infile)

        adjust_directory_permissions(
            pod_name,
            namespace,
            user_id,
        )


@contextlib.contextmanager
def pod_for_volume(
    volume_name: str,
    namespace: str,
    read_only=True,
):
    from kubernetes import client

    core_v1_api = client.CoreV1Api()

    containers = [
        client.V1Container(
            name=volume_name,
            image="alpine:latest",
            command=["sleep", "infinity"],
            volume_mounts=[
                client.V1VolumeMount(
                    name="vol",
                    mount_path=MOUNT_PATH,
                    read_only=read_only,
                )
            ],
            image_pull_policy="Always",
            resources=client.V1ResourceRequirements(
                limits={"cpu": "100m", "memory": "128Mi"},
                requests={"cpu": "100m", "memory": "128Mi"},
            ),
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
        metadata=client.V1ObjectMeta(name=volume_name),
        spec=client.V1PodSpec(
            containers=containers,
            volumes=volumes_,
            restart_policy="Never",
        ),
    )

    core_v1_api.create_namespaced_pod(namespace, pod)

    timeout = 300  # seconds
    while not is_pod_ready(volume_name, namespace) and timeout > 0:
        print("Waiting for pod to come online...")
        time.sleep(2)
        timeout -= 2

    yield volume_name

    core_v1_api.delete_namespaced_pod(volume_name, namespace)


def create_persistent_volume(
    name: str,
    namespace: str,
    access_mode: str,
    storage_class_name: str,
):
    """Rebuild a PVC, according to the config defined in
    `capellacollab/sessions/hooks/persistent_workspace.py`.
    """

    from kubernetes import client

    core_v1_api = client.CoreV1Api()

    username = (
        name[len(PERSISTENT_SESSION_PREFIX) :]
        if name.startswith(PERSISTENT_SESSION_PREFIX)
        else name
    )

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
        core_v1_api.create_namespaced_persistent_volume_claim(namespace, pvc)
    except client.exceptions.ApiException as e:
        # Persistent volume already exists
        if e.status == 409:
            print(f"Using existing volume {name}")
            return
        raise


def adjust_directory_permissions(
    pod_name: str,
    namespace: str,
    user_id: str | None,
    directory: str = MOUNT_PATH,
):
    from kubernetes import client, stream

    resp = stream.stream(
        client.CoreV1Api().connect_get_namespaced_pod_exec,
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


def is_pod_ready(pod_name, namespace):
    from kubernetes import client

    try:
        pod_status = client.CoreV1Api().read_namespaced_pod_status(
            pod_name, namespace
        )
        return pod_status.status.phase == "Running"
    except client.exceptions.ApiException as e:
        print(
            f"Exception when calling CoreV1Api->read_namespaced_pod_status: {e}"
        )
        return False


def stream_tar_from_pod(pod_name, namespace, command):
    from kubernetes import client, stream

    exec_stream = stream.stream(
        client.CoreV1Api().connect_get_namespaced_pod_exec,
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


def stream_tar_to_pod(pod_name, namespace, infile):
    from kubernetes import client, stream

    exec_stream = stream.stream(
        client.CoreV1Api().connect_get_namespaced_pod_exec,
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
        from kubernetes import stream

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
