# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import base64
import binascii
import enum
import json
import logging
import random
import shlex
import string
import typing as t
from dataclasses import dataclass
from datetime import datetime

import kubernetes
import kubernetes.config
import kubernetes.stream.stream
import yaml
from kubernetes import client
from kubernetes.client import exceptions

from capellacollab.config import config

log = logging.getLogger(__name__)

external_registry: str = config["docker"]["externalRegistry"]

cfg: dict[str, t.Any] = config["k8s"]

namespace: str = cfg["namespace"]
storage_access_mode: str = cfg["storageAccessMode"]
storage_class_name: str = cfg["storageClassName"]

loki_enabled: bool = cfg["promtail"]["lokiEnabled"]


def deserialize_kubernetes_resource(content: t.Any, resource: str):
    # This is needed as "workaround" for the deserialize function
    class FakeKubeResponse:
        def __init__(self, obj):
            self.data = json.dumps(obj)

    return client.ApiClient().deserialize(FakeKubeResponse(content), resource)


# Resolve securityContext and pullPolicy
image_pull_policy: str = cfg.get("cluster", {}).get(
    "imagePullPolicy", "Always"
)

pod_security_context = None
if _pod_security_context := cfg.get("cluster", {}).get(
    "podSecurityContext", None
):
    pod_security_context = deserialize_kubernetes_resource(
        _pod_security_context, client.V1PodSecurityContext.__name__
    )

if cfg.get("context", None):
    kubernetes.config.load_config(context=cfg.get("context", None))
elif cfg.get("apiURL", None) and cfg.get("token", None):
    kubernetes.config.load_kube_config_from_dict(
        {
            "apiVersion": "v1",
            "kind": "Config",
            "clusters": [
                {
                    "cluster": {
                        "insecure-skip-tls-verify": True,
                        "server": cfg.get("apiURL", None),
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
                    "user": {"token": cfg.get("token", None)},
                }
            ],
        }
    )
else:
    kubernetes.config.load_incluster_config()


class FileType(enum.Enum):
    FILE = "file"
    DIRECTORY = "directory"


@dataclass
class File:
    path: str
    name: str
    type: FileType
    children: list[File] | None = None


class KubernetesOperator:
    def __init__(self) -> None:
        self.v1_core = client.CoreV1Api()
        self.v1_apps = client.AppsV1Api()
        self.v1_batch = client.BatchV1Api()

    def validate(self) -> bool:
        try:
            self.v1_core.get_api_resources()
            return True
        except BaseException:
            return False

    def start_persistent_session(
        self,
        username: str,
        tool_name: str,
        version_name: str,
        password: str,
        docker_image: str,
        t4c_license_secret: str | None,
        t4c_json: list[dict[str, str | int]] | None,
        pure_variants_license_server: str | None = None,
        pure_variants_secret_name: str | None = None,
    ) -> dict[str, t.Any]:
        self._create_persistent_volume_claim(username)

        environment = {
            "T4C_LICENCE_SECRET": t4c_license_secret,
            "T4C_JSON": json.dumps(t4c_json),
            "RMT_PASSWORD": password,
            "FILESERVICE_PASSWORD": password,
            "T4C_USERNAME": username,
        }

        if pure_variants_license_server:
            environment[
                "PURE_VARIANTS_LICENSE_SERVER"
            ] = pure_variants_license_server

        return self._start_session(
            image=docker_image,
            username=username,
            session_type="persistent",
            tool_name=tool_name,
            version_name=version_name,
            environment=environment,
            persistent_workspace_claim_name=self._get_claim_name(username),
            pure_variants_secret_name=pure_variants_secret_name,
        )

    def start_readonly_session(
        self,
        username: str,
        tool_name: str,
        version_name: str,
        password: str,
        docker_image: str,
        git_repos_json: list[dict[str, str | int]],
    ) -> dict[str, t.Any]:
        return self._start_session(
            image=docker_image,
            username=username,
            session_type="readonly",
            tool_name=tool_name,
            version_name=version_name,
            environment={
                "GIT_REPOS_JSON": json.dumps(git_repos_json),
                "RMT_PASSWORD": password,
            },
        )

    def _start_session(
        self,
        image: str,
        username: str,
        session_type: str,
        tool_name: str,
        version_name: str,
        environment: dict[str, str | None],
        persistent_workspace_claim_name: str | None = None,
        pure_variants_secret_name: str | None = None,
    ) -> dict[str, t.Any]:
        log.info("Launching a %s session for user %s", session_type, username)

        _id = self._generate_id()

        if loki_enabled:
            self._create_promtail_configmap(
                name=_id,
                username=username,
                session_type=session_type,
                tool_name=tool_name,
                version_name=version_name,
            )

        deployment = self._create_deployment(
            image=image,
            name=_id,
            environment=environment,
            persistent_workspace_claim_name=persistent_workspace_claim_name,
            pure_variants_secret_name=pure_variants_secret_name,
        )

        service = self._create_service(name=_id, deployment_name=_id)

        log.info(
            "Launched a %s session for user %s with id %s",
            session_type,
            username,
            _id,
        )
        return self._export_attrs(deployment, service)

    def kill_session(self, _id: str):
        log.info("Terminating session %s", _id)

        if dep_status := self._delete_deployment(name=_id):
            log.info(
                "Deleted deployment %s with status %s", _id, dep_status.status
            )

        if loki_enabled and (conf_status := self._delete_config_map(name=_id)):
            log.info(
                "Deleted config map %s with status %s", _id, conf_status.status
            )

        if svc_status := self._delete_service(name=_id):
            log.info(
                "Deleted service %s with status %s", _id, svc_status.status
            )

    def get_job_state(self, job_name: str) -> str:
        return self._get_pod_state(label_selector=f"job-name={job_name}")

    def get_cronjob_last_state(self, name: str) -> str:
        if job_name := self._get_last_job_name_of_cronjob(name):
            return self._get_pod_state(label_selector=f"job-name={job_name}")
        return "NoJob"

    def get_cronjob_last_starting_date(self, name: str) -> datetime | None:
        if job_name := self._get_last_job_name_of_cronjob(name):
            return self._get_pod_starttime(
                label_selector=f"job-name={job_name}"
            )
        return None

    def get_job_starting_date(self, job_name: str) -> datetime | None:
        return self._get_pod_starttime(label_selector=f"job-name={job_name}")

    def _get_last_job_name_of_cronjob(self, name: str) -> str | None:
        jobs = [
            item
            for item in self.v1_batch.list_namespaced_job(
                namespace=namespace
            ).items
            if item.metadata.owner_references
            and item.metadata.owner_references[0].name == name
        ]

        if jobs:
            return jobs[-1].metadata.name
        return None

    def _get_last_job_by_label(
        self, label_key: str, label_value: str
    ) -> str | None:
        jobs = self.v1_batch.list_namespaced_job(
            namespace=namespace,
            label_selector=f"{label_key}={label_value}",
        ).items

        if jobs:
            return jobs[-1].metadata.name
        return None

    def get_session_state(self, _id: str) -> str:
        return self._get_pod_state(label_selector=f"app={_id}")

    def _get_pod_state(self, label_selector: str):
        try:
            pod = self._get_pods(label_selector=label_selector)[0]
            pod_name = pod.metadata.name

            log.debug("Received k8s pod: %s", pod_name)
            log.debug("Fetching k8s events for pod: %s", pod_name)

            events = self.v1_core.list_namespaced_event(
                namespace=namespace,
                field_selector=f"involvedObject.name={pod_name}",
            )

            if events.items:
                return events.items[-1].reason

            # Fallback if no event is available
            return pod.status.phase

        except exceptions.ApiException as e:
            log.warning("Kubernetes error", exc_info=True)
            return f"error-{str(e.status)}"
        except Exception:
            log.exception("Error getting the session state")

        return "unknown"

    def _get_pod_starttime(self, label_selector: str) -> datetime | None:
        try:
            pods: list[client.V1Pod] = self._get_pods(
                label_selector=label_selector
            )
            log.debug("Received k8s pods: %s", pods)

            return pods[0].status.start_time
        except Exception:
            log.exception("Error fetching the starting_time")
            return None

    def get_session_logs(self, _id: str) -> str:
        return self.v1_core.read_namespaced_pod_log(
            name=self._get_pod_name(_id),
            container=_id,
            namespace=namespace,
        )

    def get_job_logs_or_events(self, _id: str) -> str:
        try:
            if pod_log := self.v1_core.read_namespaced_pod_log(
                name=_id, namespace=namespace
            ):
                return pod_log
        except Exception:
            pass

        return "\n".join(
            [
                item.reason + ": " + item.message
                for item in self.v1_core.list_namespaced_event(
                    namespace=namespace,
                    field_selector=f"involvedObject.name={_id}",
                ).items
            ]
        )

    def create_cronjob(
        self,
        image: str,
        environment: dict[str, str | None],
        schedule="* * * * *",
        timeout=18000,
    ) -> str:
        _id = self._generate_id()
        self._create_cronjob(
            name=_id,
            image=image,
            job_labels={"app.capellacollab/parent": _id},
            environment=environment,
            schedule=schedule,
            timeout=timeout,
        )
        return _id

    def create_job(
        self,
        image: str,
        labels: dict[str, str],
        environment: dict[str, str | None],
        timeout: int = 18000,
    ) -> str:
        _id = self._generate_id()
        self._create_job(
            name=_id,
            image=image,
            job_labels=labels,
            environment=environment,
            timeout=timeout,
        )
        return _id

    def trigger_cronjob(self, name: str, overwrite_environment=None) -> None:
        cronjob = self.v1_batch.read_namespaced_cron_job(
            namespace=namespace, name=name
        )

        job_spec = cronjob.spec.job_template.spec
        if overwrite_environment:
            for index, env in enumerate(
                job_spec.template.spec.containers[0].env
            ):
                if env.name in overwrite_environment:
                    job_spec.template.spec.containers[0].env[index] = {
                        "name": env.name,
                        "value": overwrite_environment[env.name],
                    }

        job = client.V1Job(
            api_version="batch/v1",
            kind="Job",
            metadata=client.models.V1ObjectMeta(
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
                labels={"app.capellacollab/parent": name},
            ),
            spec=job_spec,
        )
        self.v1_batch.create_namespaced_job(namespace=namespace, body=job)

    def delete_cronjob(self, _id: str):
        try:
            self.v1_batch.delete_namespaced_cron_job(
                namespace=namespace, name=_id
            )
        except exceptions.ApiException:
            log.exception("Error deleting cronjob with name: %s", _id)

    def get_cronjob_last_run(self, name: str) -> str | None:
        if job_name := self._get_last_job_name_of_cronjob(name):
            return self._get_pod_id(label_selector=f"job-name={job_name}")
        return None

    def get_cronjob_last_run_by_label(
        self, label_key: str, label_value: str
    ) -> str | None:
        if job_name := self._get_last_job_by_label(label_key, label_value):
            return self._get_pod_id(label_selector=f"job-name={job_name}")
        return None

    def _get_pod_id(self, label_selector: str) -> str:
        try:
            pods = self.v1_core.list_namespaced_pod(
                namespace=namespace, label_selector=label_selector
            ).to_dict()
            log.debug("Received k8s pods: %s", pods)

            return pods["items"][0]["metadata"]["name"]
        except Exception:
            log.exception("Error fetching the last run id")
            return ""

    def _generate_id(self) -> str:
        return "".join(random.choices(string.ascii_lowercase, k=25))

    def _export_attrs(
        self,
        deployment: client.V1Deployment,
        service: client.V1Service,
    ) -> dict[str, t.Any]:
        return {
            "id": deployment.to_dict()["metadata"]["name"],
            "ports": {3389},
            "created_at": deployment.to_dict()["metadata"][
                "creation_timestamp"
            ],
            "mac": "-",
            "host": service.to_dict()["metadata"]["name"] + "." + namespace,
        }

    def _create_deployment(
        self,
        image: str,
        name: str,
        environment: dict[str, str | None],
        persistent_workspace_claim_name: str | None = None,
        pure_variants_secret_name: str | None = None,
    ) -> client.V1Deployment:
        volumes: list[client.V1Volume] = []
        session_volume_mounts: list[client.V1VolumeMount] = []
        promtail_volume_mounts: list[client.V1VolumeMount] = []

        if persistent_workspace_claim_name:
            volumes.append(
                client.V1Volume(
                    name="workspace",
                    persistent_volume_claim=client.V1PersistentVolumeClaimVolumeSource(
                        claim_name=persistent_workspace_claim_name
                    ),
                )
            )
        else:
            volumes.append(
                client.V1Volume(
                    name="workspace", empty_dir=client.V1EmptyDirVolumeSource()
                )
            )

        session_volume_mounts.append(
            client.V1VolumeMount(name="workspace", mount_path="/workspace")
        )

        if loki_enabled:
            promtail_volume_mounts.append(
                client.V1VolumeMount(
                    name="workspace", mount_path="/var/log/promtail"
                )
            )

            volumes.append(
                client.V1Volume(
                    name="prom-config",
                    config_map=client.V1ConfigMapVolumeSource(name=name),
                )
            )

            promtail_volume_mounts.append(
                client.V1VolumeMount(
                    name="prom-config", mount_path="/etc/promtail"
                )
            )

        if pure_variants_secret_name:
            session_volume_mounts.append(
                client.V1VolumeMount(
                    name="pure-variants",
                    mount_path="/inputs/pure-variants",
                    read_only=True,
                )
            )

            volumes.append(
                client.V1Volume(
                    name="pure-variants",
                    secret=client.V1SecretVolumeSource(
                        secret_name=pure_variants_secret_name, optional=True
                    ),
                )
            )

        containers: list[client.V1Container] = []
        containers.append(
            client.V1Container(
                name=name,
                image=image,
                ports=[
                    client.V1ContainerPort(
                        container_port=3389, protocol="TCP"
                    ),
                    client.V1ContainerPort(
                        container_port=9118, protocol="TCP"
                    ),
                    client.V1ContainerPort(
                        container_port=8000, protocol="TCP"
                    ),
                ],
                env=[
                    client.V1EnvVar(name=key, value=str(value))
                    for key, value in environment.items()
                ],
                resources=client.V1ResourceRequirements(
                    limits={"cpu": "2", "memory": "6Gi"},
                    requests={"cpu": "0.4", "memory": "1.6Gi"},
                ),
                volume_mounts=session_volume_mounts,
                image_pull_policy=image_pull_policy,
            )
        )
        if loki_enabled:
            containers.append(
                client.V1Container(
                    name="promtail",
                    image=f"{external_registry}/grafana/promtail",
                    args=[
                        "--config.file=/etc/promtail/promtail.yaml",
                        "-log-config-reverse-order",
                    ],
                    ports=[
                        client.V1ContainerPort(
                            name="metrics", container_port=3101, protocol="TCP"
                        )
                    ],
                    resources=client.V1ResourceRequirements(
                        limits={"cpu": "0.1", "memory": "50Mi"},
                        requests={"cpu": "0.05", "memory": "5Mi"},
                    ),
                    volume_mounts=promtail_volume_mounts,
                    image_pull_policy=image_pull_policy,
                )
            )

        deployment: client.V1Deployment = client.V1Deployment(
            kind="Deployment",
            api_version="apps/v1",
            metadata=client.V1ObjectMeta(name=name),
            spec=client.V1DeploymentSpec(
                replicas=1,
                selector=client.V1LabelSelector(match_labels={"app": name}),
                template=client.V1PodTemplateSpec(
                    metadata=client.V1ObjectMeta(labels={"app": name}),
                    spec=client.V1PodSpec(
                        security_context=pod_security_context,
                        containers=containers,
                        volumes=volumes,
                        restart_policy="Always",
                    ),
                ),
            ),
        )

        return self.v1_apps.create_namespaced_deployment(namespace, deployment)

    def create_secret(
        self, name: str, content: dict[str, bytes], overwrite: bool = False
    ) -> client.V1Secret:
        content_b64 = {
            key: base64.b64encode(value).decode()
            for key, value in content.items()
        }

        secret = client.V1Secret(
            api_version="v1",
            kind="Secret",
            metadata=client.V1ObjectMeta(name=name),
            data=content_b64,
        )

        if overwrite:
            self.delete_secret(name)
        return self.v1_core.create_namespaced_secret(cfg["namespace"], secret)

    def _create_cronjob(
        self,
        name: str,
        image: str,
        job_labels: dict[str, str],
        environment: dict[str, str | None],
        schedule: str = "* * * * *",
        timeout: int = 18000,
    ) -> client.V1CronJob:
        cron_job: client.V1CronJob = client.V1CronJob(
            kind="CronJob",
            api_version="batch/v1",
            metadata=client.V1ObjectMeta(name=name),
            spec=client.V1CronJobSpec(
                schedule=schedule,
                job_template=client.V1JobTemplateSpec(
                    metadata=client.V1ObjectMeta(labels=job_labels),
                    spec=self._create_job_spec(
                        name, image, job_labels, environment, timeout
                    ),
                ),
            ),
        )
        return self.v1_batch.create_namespaced_cron_job(namespace, cron_job)

    def _create_job(
        self,
        name: str,
        image: str,
        job_labels: dict[str, str],
        environment: dict[str, str | None],
        timeout=18000,
    ) -> client.V1Job:
        job: client.V1Job = client.V1Job(
            kind="Job",
            api_version="batch/v1",
            metadata=client.V1ObjectMeta(name=name),
            spec=self._create_job_spec(
                name, image, job_labels, environment, timeout
            ),
        )
        return self.v1_batch.create_namespaced_job(namespace, job)

    def _create_service(
        self, name: str, deployment_name: str
    ) -> client.V1Service:
        service: client.V1Service = client.V1Service(
            kind="Service",
            api_version="v1",
            metadata=client.V1ObjectMeta(
                name=name,
                labels={"app": name},
                annotations={
                    "prometheus.io/scrape": "true",
                    "prometheus.io/path": "/metrics",
                    "prometheus.io/port": "9118",
                },
            ),
            spec=client.V1ServiceSpec(
                ports=[
                    client.V1ServicePort(
                        name="rdp", protocol="TCP", port=3389, target_port=3389
                    ),
                    client.V1ServicePort(
                        name="metrics",
                        protocol="TCP",
                        port=9118,
                        target_port=9118,
                    ),
                    client.V1ServicePort(
                        name="fileservice",
                        protocol="TCP",
                        port=8000,
                        target_port=8000,
                    ),
                ],
                selector={"app": deployment_name},
                type="ClusterIP",
            ),
        )
        return self.v1_core.create_namespaced_service(namespace, service)

    def _create_persistent_volume_claim(self, username: str):
        pvc: client.V1PersistentVolumeClaim = client.V1PersistentVolumeClaim(
            kind="PersistentVolumeClaim",
            api_version="v1",
            metadata=client.V1ObjectMeta(name=self._get_claim_name(username)),
            spec=client.V1PersistentVolumeClaimSpec(
                access_modes=[storage_access_mode],
                storage_class_name=storage_class_name,
                resources=client.V1ResourceRequirements(
                    requests={"storage": "20Gi"}
                ),
            ),
        )

        try:
            self.v1_core.create_namespaced_persistent_volume_claim(
                namespace, pvc
            )
        except exceptions.ApiException as e:
            if e.status == 409:
                return
            raise

    def _create_job_spec(
        self,
        name: str,
        image: str,
        job_labels: dict[str, str],
        environment: dict[str, str | None],
        timeout: int = 18000,
    ) -> client.V1JobSpec:
        containers: list[client.V1Container] = [
            client.V1Container(
                name=name,
                image=image,
                env=[
                    client.V1EnvVar(name=key, value=str(value))
                    for key, value in environment.items()
                ],
                resources=client.V1ResourceRequirements(
                    limits={"cpu": "2", "memory": "6Gi"},
                    requests={"cpu": "0.4", "memory": "1.6Gi"},
                ),
                image_pull_policy=image_pull_policy,
            )
        ]

        return client.V1JobSpec(
            template=client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(labels=job_labels),
                spec=client.V1PodSpec(
                    security_context=pod_security_context,
                    containers=containers,
                    restart_policy="Never",
                ),
            ),
            backoff_limit=0,
            active_deadline_seconds=timeout,
        )

    def _create_promtail_configmap(
        self,
        name: str,
        username: str,
        session_type: str,
        tool_name: str,
        version_name: str,
    ) -> client.V1ConfigMap:
        config_map: client.V1ConfigMap = client.V1ConfigMap(
            kind="ConfigMap",
            api_version="v1",
            metadata=client.V1ObjectMeta(name=name),
            data={
                "promtail.yaml": yaml.dump(
                    {
                        "server": {
                            "http_listen_port": cfg["promtail"]["serverPort"],
                        },
                        "clients": [
                            {
                                "url": cfg["promtail"]["lokiUrl"],
                                "basic_auth": {
                                    "username": cfg["promtail"][
                                        "lokiUsername"
                                    ],
                                    "password": cfg["promtail"][
                                        "lokiPassword"
                                    ],
                                },
                            }
                        ],
                        "positions": {
                            "filename": "/var/log/promtail/positions.yaml"
                        },
                        "scrape_configs": [
                            {
                                "job_name": "system",
                                "pipeline_stages": [
                                    {
                                        "multiline": {
                                            "firstline": "^[^\t]",
                                        },
                                    }
                                ],
                                "static_configs": [
                                    {
                                        "targets": ["localhost"],
                                        "labels": {
                                            "deployment": f"{namespace}-sessions",
                                            "username": username,
                                            "session_type": session_type,
                                            "tool": tool_name,
                                            "version": version_name,
                                            "__path__": "/var/log/promtail/**/*.log",
                                        },
                                    }
                                ],
                            }
                        ],
                    }
                )
            },
        )
        return self.v1_core.create_namespaced_config_map(namespace, config_map)

    def _get_claim_name(self, username: str) -> str:
        return (
            "persistent-session-"
            + username.replace("@", "-at-").replace(".", "-dot-").lower()
        )

    def _delete_deployment(self, name: str) -> client.V1Status | None:
        try:
            return self.v1_apps.delete_namespaced_deployment(name, namespace)
        except exceptions.ApiException:
            log.exception("Error deleting deployment with name: %s", name)
            return None

    def delete_secret(self, name: str) -> kubernetes.client.V1Status | None:
        try:
            return self.v1_core.delete_namespaced_secret(name, namespace)
        except client.exceptions.ApiException:
            log.exception("Error deleting secret with name: %s", name)
            return None

    def _delete_config_map(self, name: str) -> client.V1Status | None:
        try:
            return self.v1_core.delete_namespaced_config_map(name, namespace)
        except exceptions.ApiException:
            log.exception("Error deleting config map with name: %s", name)
            return None

    def _delete_service(self, name: str) -> client.V1Status | None:
        try:
            return self.v1_core.delete_namespaced_service(name, namespace)
        except exceptions.ApiException:
            log.exception("Error deleting service with name: %s", name)
            return None

    def _get_pod_name(self, _id: str) -> str:
        return self._get_pods(label_selector=f"app={_id}")[0].metadata.name

    def _get_pods(self, label_selector: str) -> list[client.V1Pod]:
        return self.v1_core.list_namespaced_pod(
            namespace=namespace, label_selector=label_selector
        ).items

    def upload_files(
        self,
        _id: str,
        content: bytes,
    ):
        pod_name = self._get_pod_name(_id)

        try:
            exec_command = ["tar", "xf", "-", "-C", "/"]
            stream = kubernetes.stream.stream(
                self.v1_core.connect_get_namespaced_pod_exec,
                pod_name,
                namespace=namespace,
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
                log.debug(
                    "Upload into %s - STDOUT: %s", _id, stream.read_stdout()
                )
            if stream.peek_stderr():
                log.debug(
                    "Upload into %s - STDERR: %s", _id, stream.read_stderr()
                )

        except exceptions.ApiException:
            log.exception(
                "Exception when copying file to the pod with id %s", _id
            )
            raise

    def download_file(self, id: str, filename: str) -> t.Iterable[bytes]:
        pod_name = self._get_pod_name(id)
        try:
            exec_command = [
                "bash",
                "-c",
                f"zip -qr /tmp/archive.zip '{shlex.quote(filename)}' && base64 /tmp/archive.zip && rm -f /tmp/archive.zip",
            ]
            stream = kubernetes.stream.stream(
                self.v1_core.connect_get_namespaced_pod_exec,
                pod_name,
                namespace=cfg["namespace"],
                command=exec_command,
                stderr=True,
                stdin=False,
                stdout=True,
                tty=False,
                _preload_content=False,
            )

            def reader():
                while stream.is_open():
                    content = stream.read_stdout(timeout=60)
                    if content:
                        yield content.encode("utf-8")

            yield from lazy_b64decode(reader())

        except kubernetes.client.exceptions.ApiException:
            log.exception(
                "Exception when copying file to the pod with id %s", id
            )
            raise


def lazy_b64decode(reader):
    data = b""
    for b64data in reader:
        data += b64data
        try:
            yield base64.b64decode(data)
            data = b""
        except binascii.Error:
            pass
