# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

# Standard library:
import enum
import logging
import os
import pathlib
import random
import string
import typing as t
from dataclasses import dataclass
from datetime import datetime

# 3rd party:
import kubernetes
import kubernetes.client.exceptions
import kubernetes.client.models
import kubernetes.config
import kubernetes.stream.stream

# local:
from t4cclient.config import config
from t4cclient.sessions.operators.abc import Operator

log = logging.getLogger(__name__)
cfg = config["operators"]["k8s"]

try:
    kubernetes.config.load_incluster_config()
except kubernetes.config.ConfigException:
    try:
        kubernetes.config.load_config(context=cfg["context"])
    except kubernetes.config.ConfigException:
        kubernetes.config.load_kube_config_from_dict(
            {
                "apiVersion": "v1",
                "kind": "Config",
                "clusters": [
                    {
                        "cluster": {
                            "insecure-skip-tls-verify": True,
                            "server": cfg["apiURL"],
                        },
                        "name": "cluster",
                    }
                ],
                "contexts": [
                    {
                        "context": {"cluster": "cluster", "user": "tokenuser"},
                        "name": "cluster",
                    }
                ],
                "current-context": "cluster",
                "users": [
                    {
                        "name": "tokenuser",
                        "user": {"token": cfg["token"]},
                    }
                ],
            }
        )


class FileType(enum.Enum):
    FILE = "file"
    DIRECTORY = "directory"


@dataclass
class File:
    path: str
    name: str
    type: FileType
    children: t.Optional[list[File]] = None


class KubernetesOperator(Operator):
    def __init__(self) -> None:
        self.v1_core = kubernetes.client.CoreV1Api()
        self.v1_apps = kubernetes.client.AppsV1Api()
        self.v1_batch = kubernetes.client.BatchV1Api()

    def validate(self) -> str:
        try:
            self.v1_core.get_api_resources()
            return "ok"
        except:
            return "cannot connect"

    def start_persistent_session(
        self,
        username: str,
        password: str,
        repositories: t.List[str],
    ) -> t.Dict[str, t.Any]:
        log.info("Launching a persistent session for user %s", username)
        t4c_cfg = config["modelsources"]["t4c"]

        id = self._generate_id()
        self._create_persistent_volume_claim(username)
        deployment = self._create_deployment(
            config["docker"]["images"]["workspaces"]["persistent"],
            id,
            {
                "T4C_LICENCE_SECRET": t4c_cfg["licence"],
                "T4C_SERVER_HOST": t4c_cfg["host"],
                "T4C_SERVER_PORT": t4c_cfg["port"],
                "T4C_REPOSITORIES": ",".join(repositories),
                "RMT_PASSWORD": password,
                "FILESERVICE_PASSWORD": password,
                "T4C_USERNAME": username,
            },
            self._get_claim_name(username),
        )
        self._create_service(id, id)
        service = self._get_service(id)
        log.info("Launched a persistent session for user %s with id %s", username, id)
        return self._export_attrs(deployment, service)

    def start_readonly_session(
        self,
        password: str,
        git_url: str,
        git_revision: str,
        entrypoint: str,
        git_username: str,
        git_password: str,
    ) -> t.Dict[str, t.Any]:
        id = self._generate_id()

        deployment = self._create_deployment(
            config["docker"]["images"]["workspaces"]["readonly"],
            id,
            {
                "GIT_USERNAME": git_username,
                "GIT_PASSWORD": git_password,
                "GIT_URL": git_url,
                "GIT_REVISION": git_revision,
                "GIT_ENTRYPOINT": entrypoint,
                "RMT_PASSWORD": password,
            },
        )
        self._create_service(id, id)
        service = self._get_service(id)
        return self._export_attrs(deployment, service)

    def get_cronjob_last_state(self, name: str) -> str:
        job = self._get_last_job_of_cronjob(name)
        if job:
            return self._get_pod_state(label_selector="job-name=" + job)
        else:
            return "NoJob"

    def get_cronjob_last_starting_date(self, name: str) -> datetime | None:
        job = self._get_last_job_of_cronjob(name)
        if job:
            return self._get_pod_starttime(label_selector="job-name=" + job)
        else:
            return None

    def _get_last_job_of_cronjob(self, name: str) -> str | None:
        jobs = [
            item
            for item in self.v1_batch.list_namespaced_job(
                namespace=cfg["namespace"]
            ).items
            if item.metadata.owner_references
            and item.metadata.owner_references[0].name == name
        ]

        if jobs:
            return jobs[-1].metadata.name
        else:
            return None

    def get_session_state(self, id: str) -> str:
        return self._get_pod_state(label_selector="app=" + id)

    def _get_pod_state(self, label_selector: str):
        try:
            pods = self.v1_core.list_namespaced_pod(
                namespace=cfg["namespace"], label_selector=label_selector
            )

            log.debug("Received k8s pods: %s", pods.items[0].metadata.name)
            log.debug("Fetching k8s events for pod: %s", pods.items[0].metadata.name)

            return (
                self.v1_core.list_namespaced_event(
                    namespace=cfg["namespace"],
                    field_selector="involvedObject.name=" + pods.items[0].metadata.name,
                )
                .items[-1]
                .reason
            )
        except kubernetes.client.exceptions.ApiException as e:
            log.warning("Kubernetes error", exc_info=True)
            return "error-" + str(e.status)
        except Exception as e:
            log.exception("Error getting the session state")
            return "unknown"

    def _get_pod_starttime(self, label_selector: str) -> datetime | None:
        try:
            pods = self.v1_core.list_namespaced_pod(
                namespace=cfg["namespace"], label_selector=label_selector
            ).to_dict()
            log.debug("Received k8s pods: %s", pods)

            return pods["items"][0]["status"]["start_time"]
        except Exception as e:
            log.exception("Error fetching the starting_time")
            return None

    def get_session_logs(self, id: str) -> str:
        pod_name = self.v1_core.list_namespaced_pod(
            namespace=cfg["namespace"], label_selector="app=" + id
        ).to_dict()["items"][0]["metadata"]["name"]
        return self.v1_core.read_namespaced_pod_log(
            name=pod_name,
            namespace=cfg["namespace"],
        )

    def get_job_logs(self, id: str) -> str:
        try:
            log = self.v1_core.read_namespaced_pod_log(
                name=id,
                namespace=cfg["namespace"],
            )

            if log:
                return log
        except Exception:
            pass

        return "\n".join(
            [
                item.reason + ": " + item.message
                for item in self.v1_core.list_namespaced_event(
                    namespace=cfg["namespace"],
                    field_selector="involvedObject.name=" + id,
                ).items
            ]
        )

    def create_cronjob(
        self, image: str, environment: t.Dict[str, str], schedule="* * * * *"
    ) -> str:
        id = self._generate_id()
        self._create_cronjob(
            name=id,
            image=image,
            environment=environment,
            schedule=schedule,
        )
        return id

    def trigger_cronjob(self, name: str) -> None:
        cronjob = self.v1_batch.read_namespaced_cron_job(
            namespace=cfg["namespace"], name=name
        )
        job = kubernetes.client.V1Job(
            api_version="batch/v1",
            kind="Job",
            metadata=kubernetes.client.models.V1ObjectMeta(
                name=self._generate_id(),
                # This annotation is added by kubectl, probably best to add it ourselves as well
                annotations={"cronjob.kubernetes.io/instantiate": "manual"},
                owner_references=[
                    {
                        "apiVersion": "batch/v1",
                        "blockOwnerDeletion": None,
                        "controller": None,
                        "kind": "CronJob",
                        "name": name,
                        "uid": cronjob.metadata.uid,
                    }
                ],
            ),
            spec=cronjob.spec.job_template.spec,
        )
        self.v1_batch.create_namespaced_job(namespace=cfg["namespace"], body=job)

    def delete_cronjob(self, id: str) -> None:
        self._delete_cronjob(id=id)

    def get_cronjob_last_run(self, name: str) -> str | None:
        job = self._get_last_job_of_cronjob(name)
        if job:
            return self._get_pod_id(label_selector="job-name=" + job)
        else:
            return None

    def _get_pod_id(self, label_selector: str) -> str:
        try:
            pods = self.v1_core.list_namespaced_pod(
                namespace=cfg["namespace"], label_selector=label_selector
            ).to_dict()
            log.debug("Received k8s pods: %s", pods)

            return pods["items"][0]["metadata"]["name"]
        except Exception as e:
            log.exception("Error fetching the last run id")
            return ""

    def _generate_id(self):
        return "".join(random.choices(string.ascii_lowercase, k=25))

    def kill_session(self, id: str) -> None:
        log.info("Terminating session %s", id)
        status = self._delete_deployment(id)
        log.info(f"Deleted deployment {id}: {status and status.status}")
        self._delete_service(id)
        log.info(f"Deleted service {id}: {status and status.status}")

    def _export_attrs(
        self,
        deployment: kubernetes.client.V1Deployment,
        service: kubernetes.client.V1Service,
    ) -> t.Dict[str, t.Any]:
        return {
            "id": deployment.to_dict()["metadata"]["name"],
            "ports": set([3389]),
            "created_at": deployment.to_dict()["metadata"]["creation_timestamp"],
            "mac": "-",
            "host": service.to_dict()["metadata"]["name"] + "." + cfg["namespace"],
        }

    def _create_deployment(
        self,
        image: str,
        name: str,
        environment: t.Dict,
        volume_claim_name: str = None,
    ) -> kubernetes.client.V1Deployment:
        volume_mount = []
        volume = []

        if volume_claim_name:
            volume_mount.append({"name": "workspace", "mountPath": "/workspace"})

            volume.append(
                {
                    "name": "workspace",
                    "persistentVolumeClaim": {"claimName": volume_claim_name},
                }
            )

        body = {
            "kind": "Deployment",
            "apiVersion": "apps/v1",
            "metadata": {"name": name},
            "spec": {
                "replicas": 1,
                "selector": {"matchLabels": {"app": name}},
                "template": {
                    "metadata": {
                        "labels": {"app": name},
                    },
                    "spec": {
                        "containers": [
                            {
                                "name": name,
                                "image": image,
                                "ports": [
                                    {"containerPort": 3389, "protocol": "TCP"},
                                    {"containerPort": 9118, "protocol": "TCP"},
                                ],
                                "env": [
                                    {"name": key, "value": str(value)}
                                    for key, value in environment.items()
                                ],
                                "resources": {
                                    "limits": {"cpu": "2", "memory": "6Gi"},
                                    "requests": {"cpu": "0.4", "memory": "1.6Gi"},
                                },
                                "imagePullPolicy": "Always",
                                "volumeMounts": volume_mount,
                                **cfg["cluster"]["containers"],
                            },
                        ],
                        "volumes": volume,
                        "restartPolicy": "Always",
                    },
                },
            },
        }
        return self.v1_apps.create_namespaced_deployment(cfg["namespace"], body)

    def _create_cronjob(
        self, name: str, image: str, environment: t.Dict[str, str], schedule="* * * * *"
    ) -> kubernetes.client.V1CronJob:
        body = {
            "kind": "CronJob",
            "apiVersion": "batch/v1",
            "metadata": {
                "name": name,
            },
            "spec": {
                "schedule": schedule,
                "jobTemplate": {
                    "spec": {
                        "template": {
                            "spec": {
                                "containers": [
                                    {
                                        "name": name,
                                        "image": image,
                                        "imagePullPolicy": "Always",
                                        "env": [
                                            {"name": key, "value": value}
                                            for key, value in environment.items()
                                        ],
                                        "resources": {
                                            "limits": {"cpu": "2", "memory": "6Gi"},
                                            "requests": {
                                                "cpu": "0.4",
                                                "memory": "1.6Gi",
                                            },
                                        },
                                        **cfg["cluster"]["containers"],
                                    }
                                ],
                                "restartPolicy": "Never",
                            }
                        },
                        "backoffLimit": 1,
                        "activeDeadlineSeconds": 600,
                    }
                },
            },
        }

        return self.v1_batch.create_namespaced_cron_job(
            namespace=cfg["namespace"], body=body
        )

    def _create_service(
        self, name: str, deployment_name: str
    ) -> kubernetes.client.V1Service:
        body = {
            "kind": "Service",
            "apiVersion": "v1",
            "metadata": {
                "name": name,
                "labels": {"app": name},
                "annotations": {
                    "prometheus.io/scrape": "true",
                    "prometheus.io/path": "/metrics",
                    "prometheus.io/port": "9118",
                },
            },
            "spec": {
                "ports": [
                    {
                        "name": "rdp",
                        "protocol": "TCP",
                        "port": 3389,
                        "targetPort": 3389,
                    },
                    {
                        "name": "metrics",
                        "protocol": "TCP",
                        "port": 9118,
                        "targetPort": 9118,
                    },
                    {
                        "name": "fileservice",
                        "protocol": "TCP",
                        "port": 8000,
                        "targetPort": 8000,
                    },
                ],
                "selector": {"app": deployment_name},
                "type": "ClusterIP",
            },
        }
        return self.v1_core.create_namespaced_service(cfg["namespace"], body)

    def _create_persistent_volume_claim(self, username):
        body = {
            "apiVersion": "v1",
            "kind": "PersistentVolumeClaim",
            "metadata": {
                "name": self._get_claim_name(username),
            },
            "spec": {
                "accessModes": [cfg["storageAccessMode"]],
                "storageClassName": cfg["storageClassName"],
                "resources": {"requests": {"storage": "20Gi"}},
            },
        }
        try:
            self.v1_core.create_namespaced_persistent_volume_claim(
                cfg["namespace"], body
            )
        except kubernetes.client.exceptions.ApiException as e:
            if e.status == 409:
                return
            raise

    def _get_claim_name(self, username: str) -> str:
        return (
            "persistent-session-"
            + username.replace("@", "-at-").replace(".", "-dot-").lower()
        )

    def _get_service(self, id: str):
        return self.v1_core.read_namespaced_service(id, cfg["namespace"])

    def _delete_deployment(self, id: str) -> kubernetes.client.V1Status:
        try:
            return self.v1_apps.delete_namespaced_deployment(id, cfg["namespace"])
        except kubernetes.client.exceptions.ApiException:
            log.exception("Error deleting deployment with id: %s", id)

    def _delete_cronjob(self, id: str) -> kubernetes.client.V1Status:
        try:
            return self.v1_batch.delete_namespaced_cron_job(id, cfg["namespace"])
        except kubernetes.client.exceptions.ApiException:
            log.exception("Error deleting cronjob with id: %s", id)

    def _delete_service(self, id: str) -> kubernetes.client.V1Status:
        try:
            return self.v1_core.delete_namespaced_service(id, cfg["namespace"])
        except kubernetes.client.exceptions.ApiException:
            log.exception("Error deleting service with id: %s", id)

    def _get_pod_name(self, id: str) -> str:
        return self.v1_core.list_namespaced_pod(
            namespace=cfg["namespace"], label_selector="app=" + id
        ).to_dict()["items"][0]["metadata"]["name"]

    def upload_files(
        self,
        id: str,
        content: bytes,
    ):
        pod_name = self._get_pod_name(id)

        try:
            exec_command = ["tar", "xf", "-", "-C", "/"]
            stream = kubernetes.stream.stream(
                self.v1_core.connect_get_namespaced_pod_exec,
                pod_name,
                namespace=cfg["namespace"],
                command=exec_command,
                stderr=True,
                stdin=True,
                stdout=True,
                tty=False,
                _preload_content=False,
            )

            stream.write_stdin(content)
            stream.update(timeout=1)
            if stream.peek_stdout():
                log.debug("Upload into %s - STDOUT: %s", id, stream.read_stdout())
            if stream.peek_stderr():
                log.debug("Upload into %s - STDERR: %s", id, stream.read_stderr())

        except kubernetes.client.exceptions.ApiException as e:
            log.exception("Exception when copying file to the pod with id %s", id)
            raise e

    def get_files(self, id: str) -> File:
        pod_name = self._get_pod_name(id)
        return self.__get_files(
            pod_name,
            current_dir=pathlib.PurePosixPath("/workspace"),
        )

    def __get_files(self, pod_name: str, current_dir: pathlib.PurePosixPath) -> File:
        file = File(
            path=str(current_dir),
            name=current_dir.name,
            type=FileType.DIRECTORY,
            children=[],
        )

        exec_command = [
            "/bin/sh",
            "-c",
            f"ls -l {str(current_dir)}",
        ]

        response = kubernetes.stream.stream(
            self.v1_core.connect_get_namespaced_pod_exec,
            pod_name,
            namespace=cfg["namespace"],
            command=exec_command,
            stderr=True,
            stdin=False,
            stdout=True,
            tty=False,
        )

        if response:
            for line in response.splitlines()[1:]:
                splitted_line = line.split()

                path: pathlib.Path = current_dir / splitted_line[-1]
                permissions: str = splitted_line[0]

                if permissions.startswith("d"):
                    file.children.append(self.__get_files(pod_name, path))
                else:
                    file.children.append(
                        File(
                            name=path.name,
                            path=str(path),
                            type=FileType.FILE,
                        )
                    )

        return file
