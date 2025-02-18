# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import base64
import binascii
import datetime
import http
import json
import logging
import os.path
import random
import shlex
import string
import textwrap
import typing as t

import kubernetes
import kubernetes.config
import kubernetes.stream.stream
import prometheus_client
import typing_extensions as te  # codespell:ignore te
from kubernetes import client
from kubernetes.client import exceptions

from capellacollab.configuration.app import config
from capellacollab.configuration.app import models as config_models
from capellacollab.sessions import models as sessions_models
from capellacollab.sessions.files import exceptions as files_exceptions
from capellacollab.tools import models as tools_models

from . import helper, models

log = logging.getLogger(__name__)

SESSIONS_STARTED = prometheus_client.Counter(
    "backend_sessions_started", "", ("session_type",)
)
SESSIONS_KILLED = prometheus_client.Counter(
    "backend_sessions_killed", "Sessions killed, either by user or timeout"
)

cfg: config_models.K8sConfig = config.k8s

namespace: str = cfg.namespace

image_pull_policy: str = cfg.cluster.image_pull_policy

pod_security_context = None
if _pod_security_context := cfg.cluster.pod_security_context:
    pod_security_context = client.V1PodSecurityContext(
        **_pod_security_context.__dict__
    )


class Session(te.TypedDict):  # codespell:ignore te
    id: str
    port: int
    created_at: datetime.datetime
    host: str


class KubernetesOperator:
    def __init__(self) -> None:
        self.load_config()
        self.client = client.ApiClient()
        self.v1_core = client.CoreV1Api(api_client=self.client)
        self.v1_apps = client.AppsV1Api(api_client=self.client)
        self.v1_batch = client.BatchV1Api(api_client=self.client)
        self.v1_networking = client.NetworkingV1Api(api_client=self.client)
        self.v1_policy = client.PolicyV1Api(api_client=self.client)

    def load_config(self) -> None:
        if cfg.context:
            kubernetes.config.load_config(context=cfg.context)
        else:
            kubernetes.config.load_incluster_config()

    def validate(self) -> bool:
        try:
            self.v1_core.get_api_resources()
            return True
        except BaseException:
            return False

    def start_session(
        self,
        session_id: str,
        image: str,
        username: str,
        session_type: sessions_models.SessionType,
        tool: tools_models.DatabaseTool,
        environment: dict[str, str],
        init_environment: dict[str, str],
        ports: dict[str, int],
        volumes: list[models.Volume],
        init_volumes: list[models.Volume],
        annotations: dict[str, str],
        labels: dict[str, str],
        prometheus_path="/metrics",
        prometheus_port=9118,
    ) -> Session:
        log.info(
            "Launching a %s session for user %s", session_type.value, username
        )

        pod = self._create_session_pod(
            image=image,
            name=session_id,
            environment=environment,
            init_environment=init_environment,
            ports=ports,
            volumes=volumes,
            init_volumes=init_volumes,
            tool_resources=tool.config.resources,
            annotations=annotations,
            labels=labels,
        )

        self._create_session_disruption_budget(
            session_id=session_id,
        )

        service = self._create_session_service(
            session_id=session_id,
            ports=ports,
            prometheus_path=prometheus_path,
            prometheus_port=prometheus_port,
            annotations=annotations,
            labels=labels,
        )

        log.info(
            "Launched a %s session for user %s with id %s",
            session_type,
            username,
            session_id,
        )
        SESSIONS_STARTED.labels(session_type).inc()

        return self._export_attrs(pod, service, ports)

    def kill_session(self, _id: str):
        log.info("Terminating session %s", _id)

        self._delete_pod(name=_id)
        self._delete_disruptionbudget(name=_id)
        self._delete_service(name=_id)

        SESSIONS_KILLED.inc()

    def get_job_by_name(self, name: str) -> client.V1Job:
        return self.v1_batch.read_namespaced_job(name, namespace=namespace)

    def get_session_state(
        self, session_id: str
    ) -> tuple[
        sessions_models.SessionPreparationState,
        sessions_models.SessionState,
    ]:
        try:
            pod = self.get_pod_by_name(session_id)
        except exceptions.ApiException:
            log.warning("Error while getting session pod", exc_info=True)
            return (
                sessions_models.SessionPreparationState.UNKNOWN,
                sessions_models.SessionState.UNKNOWN,
            )

        if not pod:
            return (
                sessions_models.SessionPreparationState.NOT_FOUND,
                sessions_models.SessionState.NOT_FOUND,
            )

        status: client.V1PodStatus = pod.status
        return (
            self._get_init_container_state(status),
            self._get_container_state(status),
        )

    def _get_init_container_state(
        self,
        status: client.V1PodStatus,
    ) -> sessions_models.SessionPreparationState:
        if status.init_container_statuses:
            state: client.V1ContainerState = status.init_container_statuses[
                0
            ].state
            if state.running:
                return sessions_models.SessionPreparationState.RUNNING
            if state.waiting:
                waiting: client.V1ContainerStateWaiting = state.waiting

                # https://github.com/kubernetes/kubernetes/blob/da215bf06a3b8ac3da4e0adb110dc5acc7f61fe1/pkg/kubelet/kubelet_pods.go#L83
                if waiting.reason in ("ContainerCreating", "PodInitializing"):
                    return sessions_models.SessionPreparationState.PENDING

                # Handle errors like ImagePullBackOff properly
                return sessions_models.SessionPreparationState.FAILED
            if state.terminated:
                terminated: client.V1ContainerStateTerminated = (
                    state.terminated
                )
                if terminated.reason == "Completed":
                    return sessions_models.SessionPreparationState.COMPLETED
                if terminated.reason == "Error":
                    return sessions_models.SessionPreparationState.FAILED

        return sessions_models.SessionPreparationState.UNKNOWN

    def _get_container_state(
        self,
        status: client.V1PodStatus,
    ) -> sessions_models.SessionState:
        if status.container_statuses:
            container_statuses = [
                container_status
                for container_status in status.container_statuses
                if container_status.name == "session"
            ]
            if not container_statuses:
                return sessions_models.SessionState.UNKNOWN

            state: client.V1ContainerState = container_statuses[0].state

            if state.running:
                return sessions_models.SessionState.RUNNING
            if state.waiting:
                waiting: client.V1ContainerStateWaiting = state.waiting

                # https://github.com/kubernetes/kubernetes/blob/da215bf06a3b8ac3da4e0adb110dc5acc7f61fe1/pkg/kubelet/kubelet_pods.go#L83
                if waiting.reason in ("ContainerCreating", "PodInitializing"):
                    return sessions_models.SessionState.PENDING

                # Handle errors like ImagePullBackOff properly
                return sessions_models.SessionState.FAILED
            if state.terminated:
                return sessions_models.SessionState.TERMINATED

        return sessions_models.SessionState.UNKNOWN

    def get_job_logs(self, name: str) -> str | None:
        pod_name = self.get_pod_name_from_job_name(name)
        try:
            if pod_log := self.v1_core.read_namespaced_pod_log(
                name=pod_name,
                namespace=namespace,
                pretty=True,
                timestamps=True,
            ):
                return pod_log
        except Exception:
            log.exception("Failed fetching logs from Kubernetes")
        return None

    def get_events_for_involved_object(
        self, name: str
    ) -> list[client.CoreV1Event]:
        return self.v1_core.list_namespaced_event(
            namespace=namespace,
            field_selector=f"involvedObject.name={name}",
        ).items

    def create_cronjob(
        self,
        image: str,
        command: str,
        labels: dict[str, str],
        tool_resources: tools_models.Resources,
        environment: dict[str, str | None],
        schedule="* * * * *",
        timezone="UTC",
        timeout=18000,
    ) -> str:
        _id = self._generate_id()

        cronjob: client.V1CronJob = client.V1CronJob(
            kind="CronJob",
            api_version="batch/v1",
            metadata=client.V1ObjectMeta(name=_id, labels=labels),
            spec=client.V1CronJobSpec(
                schedule=schedule,
                time_zone=timezone,
                job_template=client.V1JobTemplateSpec(
                    metadata=client.V1ObjectMeta(labels=labels),
                    spec=self._create_job_spec(
                        name=_id,
                        image=image,
                        job_labels=labels
                        | {
                            "capellacollab/workload": "cronjob",
                            "capellacollab/parent": _id,
                        },
                        environment=environment,
                        tool_resources=tool_resources,
                        args=[command],
                        timeout=timeout,
                    ),
                ),
            ),
        )
        self.v1_batch.create_namespaced_cron_job(namespace, cronjob)
        return _id

    def create_job(
        self,
        image: str,
        command: str,
        labels: dict[str, str],
        environment: dict[str, str | None],
        tool_resources: tools_models.Resources,
        timeout: int = 18000,
    ) -> str:
        _id = self._generate_id()

        job: client.V1Job = client.V1Job(
            kind="Job",
            api_version="batch/v1",
            metadata=client.V1ObjectMeta(name=_id),
            spec=self._create_job_spec(
                name=_id,
                image=image,
                job_labels={"capellacollab/workload": "job", **labels},
                environment=environment,
                tool_resources=tool_resources,
                args=[command],
                timeout=timeout,
            ),
        )
        self.v1_batch.create_namespaced_job(namespace, job)
        return _id

    def delete_cronjob(self, _id: str):
        try:
            self.v1_batch.delete_namespaced_cron_job(
                namespace=namespace, name=_id
            )
        except exceptions.ApiException as e:
            # Cronjob doesn't exist or was already deleted
            # Nothing to do
            if e.status == http.HTTPStatus.NOT_FOUND:
                return
            raise

    def delete_job(self, name: str):
        log.info("Deleting job '%s' in cluster", name)
        try:
            self.v1_batch.delete_namespaced_job(
                namespace=namespace, name=name, propagation_policy="Background"
            )
        except exceptions.ApiException as e:
            # Job doesn't exist or was already deleted
            # Nothing to do
            if e.status == http.HTTPStatus.NOT_FOUND:
                return
            raise

    def get_pod_name_from_job_name(self, job_name: str) -> str | None:
        return self._get_pod_id(label_selector=f"job-name={job_name}")

    def get_pod_for_job(self, job_name: str) -> client.V1Pod:
        pods = self.v1_core.list_namespaced_pod(
            namespace=namespace, label_selector=f"job-name={job_name}"
        )
        if len(pods.items) == 1:
            return pods.items[0]
        return None

    def _get_pod_id(self, label_selector: str) -> str:
        try:
            pods = self.v1_core.list_namespaced_pod(
                namespace=namespace, label_selector=label_selector
            ).to_dict()

            return pods["items"][0]["metadata"]["name"]
        except Exception:
            log.exception("Error fetching the Pod ID")
            return ""

    def _generate_id(self) -> str:
        return "".join(random.choices(string.ascii_lowercase, k=25))

    def _export_attrs(
        self,
        pod: client.V1Pod,
        service: client.V1Service,
        ports: dict[str, int],
    ) -> Session:
        if "rdp" in ports:
            port = ports["rdp"]
        elif "http" in ports:
            port = ports["http"]
        else:
            raise ValueError(
                "No rdp or http port defined on the deployed session"
            )

        return Session(
            id=pod.to_dict()["metadata"]["name"],
            port=port,
            created_at=pod.to_dict()["metadata"]["creation_timestamp"],
            host=service.to_dict()["metadata"]["name"] + "." + namespace,
        )

    def _map_volumes_to_k8s_volumes(
        self,
        volumes: list[models.Volume],
    ) -> tuple[list[client.V1Volume], list[client.V1VolumeMount]]:
        k8s_volumes: list[client.V1Volume] = []
        k8s_volume_mounts: list[client.V1VolumeMount] = []

        for volume in volumes:
            k8s_volumes.append(self._map_volume_to_k8s_volume(volume))

            k8s_volume_mounts.append(
                client.V1VolumeMount(
                    name=volume.name,
                    mount_path=str(volume.container_path),
                    read_only=volume.read_only,
                    sub_path=volume.sub_path,
                )
            )

        return k8s_volumes, k8s_volume_mounts

    def _map_volume_to_k8s_volume(self, volume: models.Volume):
        match volume:
            case models.PersistentVolume():
                return client.V1Volume(
                    name=volume.name,
                    persistent_volume_claim=client.V1PersistentVolumeClaimVolumeSource(
                        claim_name=volume.volume_name
                    ),
                )
            case models.EmptyVolume():
                return client.V1Volume(
                    name=volume.name,
                    empty_dir=client.V1EmptyDirVolumeSource(),
                )
            case models.SecretReferenceVolume():
                return client.V1Volume(
                    name=volume.name,
                    secret=client.V1SecretVolumeSource(
                        secret_name=volume.secret_name,
                        optional=volume.optional,
                    ),
                )
            case models.ConfigMapReferenceVolume():
                return client.V1Volume(
                    name=volume.name,
                    config_map=client.V1ConfigMapVolumeSource(
                        name=volume.config_map_name, optional=volume.optional
                    ),
                )
            case _:
                raise KeyError(
                    f"The Kubernetes operator encountered an unsupported session volume type '{type(volume)}'"
                )

    def create_network_policy_from_pod_to_label(
        self,
        name: str,
        match_labels_from: dict[str, str],
        match_labels_to: dict[str, str],
    ):
        return self.v1_networking.create_namespaced_network_policy(
            namespace,
            client.V1NetworkPolicy(
                kind="NetworkPolicy",
                api_version="networking.k8s.io/v1",
                metadata=client.V1ObjectMeta(name=name),
                spec=client.V1NetworkPolicySpec(
                    pod_selector=client.V1LabelSelector(
                        match_labels=match_labels_to
                    ),
                    policy_types=["Ingress"],
                    ingress=[
                        client.V1NetworkPolicyIngressRule(
                            _from=[
                                client.V1NetworkPolicyPeer(
                                    pod_selector=client.V1LabelSelector(
                                        match_labels=match_labels_from
                                    )
                                )
                            ],
                        )
                    ],
                ),
            ),
        )

    def delete_network_policy(self, name: str):
        try:
            self.v1_networking.delete_namespaced_network_policy(
                name,
                namespace,
            )
        except exceptions.ApiException as e:
            # Network policy doesn't exist or was already deleted
            # Nothing to do
            if e.status == http.HTTPStatus.NOT_FOUND:
                return
            raise

    def _create_sidecar_pod(
        self,
        image: str,
        name: str,
        labels: dict[str, str],
        volumes: list[models.Volume],
        args: list[str] | None = None,
    ):
        k8s_volumes, k8s_volume_mounts = self._map_volumes_to_k8s_volumes(
            volumes
        )

        pod: client.V1Pod = client.V1Pod(
            metadata=client.V1ObjectMeta(
                name=name,
                labels=labels,
            ),
            spec=client.V1PodSpec(
                automount_service_account_token=False,
                security_context=pod_security_context,
                node_selector=cfg.cluster.node_selector,
                containers=[
                    client.V1Container(
                        name=name,
                        image=image,
                        args=args,
                        resources=client.V1ResourceRequirements(
                            limits={"cpu": "0.1", "memory": "50Mi"},
                            requests={"cpu": "0.05", "memory": "5Mi"},
                        ),
                        volume_mounts=k8s_volume_mounts,
                        image_pull_policy=image_pull_policy,
                    )
                ],
                volumes=k8s_volumes,
                restart_policy="Always",
            ),
        )

        return self.v1_core.create_namespaced_pod(namespace, pod)

    def _create_session_pod(
        self,
        image: str,
        name: str,
        environment: dict[str, str],
        init_environment: dict[str, str],
        ports: dict[str, int],
        volumes: list[models.Volume],
        init_volumes: list[models.Volume],
        tool_resources: tools_models.Resources,
        annotations: dict[str, str],
        labels: dict[str, str],
    ) -> client.V1Pod:
        k8s_volumes, k8s_volume_mounts = self._map_volumes_to_k8s_volumes(
            volumes
        )

        _, init_k8s_volume_mounts = self._map_volumes_to_k8s_volumes(
            init_volumes
        )

        resources = client.V1ResourceRequirements(
            limits={
                "cpu": tool_resources.cpu.limits,
                "memory": tool_resources.memory.limits,
            },
            requests={
                "cpu": tool_resources.cpu.requests,
                "memory": tool_resources.memory.requests,
            },
        )

        pod: client.V1Pod = client.V1Pod(
            metadata=client.V1ObjectMeta(
                name=name,
                labels=labels,
                annotations=annotations,
            ),
            spec=client.V1PodSpec(
                automount_service_account_token=False,
                security_context=pod_security_context,
                node_selector=cfg.cluster.node_selector,
                containers=[
                    client.V1Container(
                        name="session",
                        image=image,
                        ports=[
                            client.V1ContainerPort(
                                container_port=port, protocol="TCP"
                            )
                            for port in ports.values()
                        ],
                        env=self._transform_env_to_k8s_env(environment),
                        resources=resources,
                        volume_mounts=k8s_volume_mounts,
                        image_pull_policy=image_pull_policy,
                    )
                ],
                init_containers=[
                    client.V1Container(
                        name="session-preparation",
                        image=config.docker.registry
                        + "/session-preparation:"
                        + config.docker.tag,
                        env=self._transform_env_to_k8s_env(init_environment),
                        resources=resources,
                        volume_mounts=init_k8s_volume_mounts,
                        image_pull_policy=image_pull_policy,
                    )
                ],
                volumes=k8s_volumes,
                restart_policy="Never",
            ),
        )

        return self.v1_core.create_namespaced_pod(namespace, pod)

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
        return self.v1_core.create_namespaced_secret(cfg.namespace, secret)

    def _create_session_disruption_budget(
        self, session_id: str
    ) -> client.V1PodDisruptionBudget:
        """Disallow any pod description for the Pod

        If the Pod uses the recreate strategy together with
        this budget, the cluster operator shall consult the administrator before
        termination of the deployment.

        More information:
        https://kubernetes.io/docs/tasks/run-application/configure-pdb/
        """

        disruption_budget: client.V1PodDisruptionBudget = (
            client.V1PodDisruptionBudget(
                kind="PodDisruptionBudget",
                api_version="policy/v1",
                metadata=client.V1ObjectMeta(
                    name=session_id,
                    labels={"capellacollab/session-id": session_id},
                ),
                spec=client.V1PodDisruptionBudgetSpec(
                    max_unavailable=0,
                    selector=client.V1LabelSelector(
                        match_labels={
                            "capellacollab/session-id": session_id,
                            "capellacollab/workload": "session",
                        }
                    ),
                ),
            )
        )
        return self.v1_policy.create_namespaced_pod_disruption_budget(
            namespace, disruption_budget
        )

    def _create_session_service(
        self,
        session_id: str,
        ports: dict[str, int],
        prometheus_path: str,
        prometheus_port: int,
        annotations: dict[str, str],
        labels: dict[str, str],
    ) -> client.V1Service:
        service: client.V1Service = client.V1Service(
            kind="Service",
            api_version="v1",
            metadata=client.V1ObjectMeta(
                name=session_id,
                labels=labels,
                annotations={
                    "prometheus.io/scrape": "true",
                    "prometheus.io/path": prometheus_path,
                    "prometheus.io/port": f"{prometheus_port}",
                    **annotations,
                },
            ),
            spec=client.V1ServiceSpec(
                ports=[
                    client.V1ServicePort(
                        name=name,
                        protocol="TCP",
                        port=80 if name == "http" else port,
                        target_port=port,
                    )
                    for name, port in ports.items()
                ],
                selector={
                    "capellacollab/session-id": session_id,
                    "capellacollab/workload": "session",
                },
                type="ClusterIP",
            ),
        )
        return self.v1_core.create_namespaced_service(namespace, service)

    def persistent_volume_exists(self, name: str) -> bool:
        try:
            self.v1_core.read_namespaced_persistent_volume_claim(
                name=name, namespace=namespace
            )
        except exceptions.ApiException as e:
            if e.status == 404:
                return False
            raise

        return True

    def create_persistent_volume(
        self,
        name: str,
        size: str,
        labels: dict[str, str] | None = None,
        annotations: dict[str, str] | None = None,
    ):
        pvc: client.V1PersistentVolumeClaim = client.V1PersistentVolumeClaim(
            kind="PersistentVolumeClaim",
            api_version="v1",
            metadata=client.V1ObjectMeta(
                name=name, labels=labels, annotations=annotations
            ),
            spec=client.V1PersistentVolumeClaimSpec(
                access_modes=[cfg.storage_access_mode],
                storage_class_name=cfg.storage_class_name,
                resources=client.V1ResourceRequirements(
                    requests={"storage": size}
                ),
            ),
        )

        try:
            self.v1_core.create_namespaced_persistent_volume_claim(
                namespace, pvc
            )
        except exceptions.ApiException as e:
            # Persistent volume already exists
            if e.status == 409:
                return
            raise

    def delete_persistent_volume(self, name: str):
        try:
            self.v1_core.delete_namespaced_persistent_volume_claim(
                name=name, namespace=namespace
            )
        except exceptions.ApiException as e:
            # Persistent volume doesn't exist or was already deleted
            # Nothing to do
            if e.status == http.HTTPStatus.NOT_FOUND:
                return
            raise

    def _create_job_spec(
        self,
        name: str,
        image: str,
        job_labels: dict[str, str],
        environment: dict[str, str | None],
        tool_resources: tools_models.Resources,
        args: list[str] | None = None,
        timeout: int = 18000,
    ) -> client.V1JobSpec:
        resources = client.V1ResourceRequirements(
            limits={
                "cpu": tool_resources.cpu.limits,
                "memory": tool_resources.memory.limits,
            },
            requests={
                "cpu": tool_resources.cpu.requests,
                "memory": tool_resources.memory.requests,
            },
        )

        containers: list[client.V1Container] = [
            client.V1Container(
                name=name,
                image=image,
                args=args,
                env=self._transform_env_to_k8s_env(environment),
                resources=resources,
                image_pull_policy=image_pull_policy,
            )
        ]
        return client.V1JobSpec(
            template=client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(labels=job_labels),
                spec=client.V1PodSpec(
                    security_context=pod_security_context,
                    node_selector=cfg.cluster.node_selector,
                    containers=containers,
                    restart_policy="Never",
                ),
            ),
            ttl_seconds_after_finished=3600,  # Keep job for one hour, we'll handle the deletion on our own.
            backoff_limit=0,
            active_deadline_seconds=timeout,
        )

    @classmethod
    def _transform_env_to_k8s_env(
        cls, environment: t.Mapping[str, str | None]
    ) -> list[client.V1EnvVar]:
        return [
            client.V1EnvVar(name=key, value=str(value))
            for key, value in environment.items()
        ]

    def _create_configmap(
        self,
        name: str,
        data: dict,
    ) -> client.V1ConfigMap | None:
        config_map: client.V1ConfigMap = client.V1ConfigMap(
            kind="ConfigMap",
            api_version="v1",
            metadata=client.V1ObjectMeta(name=name),
            data=data,
        )
        return self.v1_core.create_namespaced_config_map(namespace, config_map)

    def _delete_pod(self, name: str) -> client.V1Status | None:
        try:
            status: client.V1Status = self.v1_core.delete_namespaced_pod(
                name, namespace
            )
            log.debug("Deleted Pod %s with status %s", name, status.status)
            return status
        except exceptions.ApiException as e:
            # Pod doesn't exist or was already deleted
            # Nothing to do
            if e.status == http.HTTPStatus.NOT_FOUND:
                return None
            raise

    def delete_secret(self, name: str) -> kubernetes.client.V1Status | None:
        try:
            return self.v1_core.delete_namespaced_secret(name, namespace)
        except exceptions.ApiException as e:
            # Secret doesn't exist or was already deleted
            # Nothing to do
            if e.status == http.HTTPStatus.NOT_FOUND:
                return None
            raise

    def _delete_config_map(self, name: str) -> client.V1Status | None:
        try:
            status: client.V1Status = (
                self.v1_core.delete_namespaced_config_map(name, namespace)
            )
            log.debug(
                "Deleted config map %s with status %s", name, status.status
            )
            return status
        except exceptions.ApiException as e:
            # Config map doesn't exist or was already deleted
            # Nothing to do
            if e.status == http.HTTPStatus.NOT_FOUND:
                return None
            raise

    def _delete_service(self, name: str) -> client.V1Status | None:
        try:
            status: client.V1Status = self.v1_core.delete_namespaced_service(
                name, namespace
            )
            log.debug("Deleted service %s with status %s", name, status.status)
            return status
        except exceptions.ApiException as e:
            # Service doesn't exist or was already deleted
            # Nothing to do
            if e.status == http.HTTPStatus.NOT_FOUND:
                return None
            raise

    def _delete_disruptionbudget(self, name: str) -> client.V1Status | None:
        try:
            status: client.V1Status = (
                self.v1_policy.delete_namespaced_pod_disruption_budget(
                    name, namespace
                )
            )
            log.debug(
                "Deleted Pod disruption budget %s with status %s",
                name,
                status.status,
            )
            return status
        except exceptions.ApiException as e:
            # Pod disruption budget doesn't exist or was already deleted
            # Nothing to do
            if e.status == http.HTTPStatus.NOT_FOUND:
                return None
            raise

    def get_pods(self, label_selector: str | None) -> list[client.V1Pod]:
        return self.v1_core.list_namespaced_pod(
            namespace=namespace, label_selector=label_selector
        ).items

    def get_pod_by_name(self, name: str) -> client.V1Pod:
        try:
            return self.v1_core.read_namespaced_pod(
                namespace=namespace, name=name
            )
        except exceptions.ApiException as e:
            if e.status == http.HTTPStatus.NOT_FOUND:
                return None
            raise

    def list_files(self, session_id: str, directory: str, show_hidden: bool):
        def print_file_tree_as_json():
            import json
            import pathlib
            import sys

            print(  # noqa: T201
                "Using CLI arguments: " + str(sys.argv[1:]), file=sys.stderr
            )

            def get_files(dir: pathlib.Path, show_hidden: bool):
                file = {
                    "path": str(dir.absolute()),
                    "name": dir.name,
                    "type": "directory",
                    "children": [],
                }

                assert isinstance(file["children"], list)

                for item in dir.iterdir():
                    if not show_hidden and item.name.startswith("."):
                        continue
                    if item.is_dir():
                        file["children"].append(get_files(item, show_hidden))
                    elif item.is_file():
                        file["children"].append(
                            {
                                "name": item.name,
                                "path": str(item.absolute()),
                                "type": "file",
                            }
                        )

                return file

            print(  # noqa: T201
                json.dumps(
                    get_files(
                        pathlib.Path(sys.argv[1]), json.loads(sys.argv[2])
                    )
                )
            )

        source = helper.get_source_of_python_function(print_file_tree_as_json)
        encoded = base64.b64encode(source.encode("utf-8")).decode("utf-8")
        command = [
            "bash",
            "-c",
            f'echo "{encoded}" | base64 --decode | python - {directory} {json.dumps(show_hidden)}',
        ]

        stdout = self._open_session_stream(
            session_id,
            command,
            None,
        )

        return json.loads(stdout)

    def _open_session_stream(
        self, session_id: str, command: list[str], stdin: bytes | None
    ) -> str:
        """Open session stream and return stdout"""

        log.debug(
            "Running command in session %s\n%s",
            session_id,
            textwrap.indent(
                " ".join(command),
                "[COMMAND] ",
            ),
        )
        try:
            stream = kubernetes.stream.stream(
                self.v1_core.connect_get_namespaced_pod_exec,
                session_id,
                container="session",
                namespace=namespace,
                command=command,
                stderr=True,
                stdin=bool(stdin),
                stdout=True,
                tty=False,
                _preload_content=False,
            )

            if stdin:
                stream.write_stdin(stdin)

            stdout = ""
            stderr = ""

            while stream.is_open():
                stream.update(timeout=1)
                if stream.peek_stdout():
                    new_stdout = stream.read_stdout()
                    stdout += new_stdout
                    log.debug(
                        "Reading STDOUT from session %s:\n%s",
                        session_id,
                        textwrap.indent(
                            new_stdout,
                            "[STDOUT] ",
                        ),
                    )
                if stream.peek_stderr():
                    new_stderr = stream.read_stderr()
                    stderr += new_stderr
                    log.debug(
                        "Reading STDERR from session %s:\n%s",
                        session_id,
                        textwrap.indent(
                            new_stderr,
                            "[STDERR] ",
                        ),
                    )
                    log.debug(
                        "Loading files of session '%s' - STDERR: %s",
                        session_id,
                        stderr,
                    )
        except exceptions.ApiException:
            logging.exception(
                "Command failed for session %s. See stacktrace below.\n%s\n%s",
                session_id,
                textwrap.indent(
                    " ".join(command),
                    "[COMMAND] ",
                ),
                textwrap.indent(
                    stderr,
                    "[STDERR] ",
                ),
            )
            raise

        return stdout

    def upload_files(
        self,
        session_id: str,
        content: bytes,
    ) -> None:
        self._open_session_stream(
            session_id, ["tar", "xf", "-", "-C", "/"], content
        )

    def download_file(self, session_id: str, path: str) -> t.Iterable[bytes]:
        try:
            exec_command = [
                "bash",
                "-c",
                f"zip -qr - {shlex.quote(path)} | base64",
            ]
            stream = kubernetes.stream.stream(
                self.v1_core.connect_get_namespaced_pod_exec,
                session_id,
                container="session",
                namespace=cfg.namespace,
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
                "Exception when copying file to the pod with id %s", session_id
            )
            raise

    def delete_file(self, session_id: str, path: str):
        normalized_path = os.path.normpath(path)
        if not normalized_path.startswith("/workspace/"):
            raise files_exceptions.FileDeletionNotAllowedError()

        self._open_session_stream(
            session_id,
            ["rm", "-rf", path],
            None,
        )


def lazy_b64decode(reader):
    data = b""
    for b64data in reader:
        data += b64data
        try:
            yield base64.b64decode(data)
            data = b""
        except binascii.Error:
            pass
