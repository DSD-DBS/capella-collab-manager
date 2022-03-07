from __future__ import annotations

import logging
import random
import string
import typing as t
from datetime import datetime

import kubernetes
import kubernetes.client.exceptions
import kubernetes.client.models
import kubernetes.config
from t4cclient import config
from t4cclient.core.operators.abc import Operator

log = logging.getLogger(__name__)

try:
    kubernetes.config.load_incluster_config()
except kubernetes.config.ConfigException:
    try:
        kubernetes.config.load_config(context=config.KUBERNETES_CONTEXT)
    except kubernetes.config.ConfigException:
        kubernetes.config.load_kube_config_from_dict(
            {
                "apiVersion": "v1",
                "kind": "Config",
                "clusters": [
                    {
                        "cluster": {
                            "insecure-skip-tls-verify": True,
                            "server": config.KUBERNETES_API_URL,
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
                        "user": {"token": config.KUBERNETES_TOKEN},
                    }
                ],
            }
        )


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

        id = self._generate_id()
        self._create_persistent_volume_claim(username)
        deployment = self._create_deployment(
            config.PERSISTENT_IMAGE,
            id,
            {
                "T4C_LICENCE_SECRET": config.T4C_LICENCE,
                "T4C_SERVER_HOST": config.T4C_SERVER_HOST,
                "T4C_SERVER_PORT": config.T4C_SERVER_PORT,
                "T4C_REPOSITORIES": ",".join(repositories),
                "RMT_PASSWORD": password,
            },
            self._get_claim_name(username),
        )
        self._create_service(id, id)
        service = self._get_service(id)
        log.info("Launched a persistent session for user %s with id %s", username, id)
        return self._export_attrs(deployment, service)

    def start_readonly_session(
        self, password: str, git_url: str, git_revision: str, entrypoint: str
    ) -> t.Dict[str, t.Any]:
        id = self._generate_id()
        deployment = self._create_deployment(
            config.READONLY_IMAGE,
            id,
            {
                "GIT_USERNAME": config.GIT_USERNAME,
                "GIT_PASSWORD": config.GIT_PASSWORD,
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
            return "pending"

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
                namespace=config.KUBERNETES_NAMESPACE
            ).items
            if item.metadata.owner_references
            and item.metadata.owner_references[0].name == name
        ]

        if jobs:
            return jobs[-1].metadata.name
        else:
            return None

    def get_session_state(self, id: str) -> str:
        self._get_pod_state(self, label_selector="app=" + id)

    def _get_pod_state(self, label_selector: str):
        try:
            pods = self.v1_core.list_namespaced_pod(
                namespace=config.KUBERNETES_NAMESPACE, label_selector=label_selector
            ).to_dict()

            log.debug("Receive k8s pod: %s", pods)
            try:
                phase = pods["items"][0]["status"]["phase"]
            except IndexError:
                return "NOT_FOUND"
            if phase == "Running":
                return "Running"
            elif phase == "Pending":
                status = pods["items"][0]["status"]

                conditions = status["conditions"]
                if conditions and conditions[-1]["reason"]:
                    return conditions[-1]["reason"]

                container_statuses = status["container_statuses"]
                if container_statuses:
                    return container_statuses[-1]["state"]["waiting"]["reason"]

            return "unknown"
        except kubernetes.client.exceptions.ApiException as e:
            log.warning("Kubernetes error", exc_info=True)
            return "error-" + str(e.status)
        except Exception as e:
            log.exception("Error parsing the session state")
            return "unknown"

    def _get_pod_starttime(self, label_selector: str) -> datetime | None:
        try:
            pods = self.v1_core.list_namespaced_pod(
                namespace=config.KUBERNETES_NAMESPACE, label_selector=label_selector
            ).to_dict()
            log.debug("Received k8s pods: %s", pods)

            return pods["items"][0]["status"]["start_time"]
        except Exception as e:
            log.exception("Error fetching the starting_time")
            return None

    def get_session_logs(self, id: str) -> str:
        pod_name = self.v1_core.list_namespaced_pod(
            namespace=config.KUBERNETES_NAMESPACE, label_selector="app=" + id
        ).to_dict()["items"][0]["metadata"]["name"]
        return self.v1_core.read_namespaced_pod_log(
            name=pod_name,
            namespace=config.KUBERNETES_NAMESPACE,
        )

    def get_job_logs(self, id: str) -> str:
        try:
            log = self.v1_core.read_namespaced_pod_log(
                name=id,
                namespace=config.KUBERNETES_NAMESPACE,
            )

            if log:
                return log
        except Exception:
            pass

        return "\n".join(
            [
                item.reason + ": " + item.message
                for item in self.v1_core.list_namespaced_event(
                    namespace=config.KUBERNETES_NAMESPACE,
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
            namespace=config.KUBERNETES_NAMESPACE, name=name
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
        self.v1_batch.create_namespaced_job(
            namespace=config.KUBERNETES_NAMESPACE, body=job
        )

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
                namespace=config.KUBERNETES_NAMESPACE, label_selector=label_selector
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
            "host": service.to_dict()["metadata"]["name"]
            + "."
            + config.KUBERNETES_NAMESPACE,
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
                    "metadata": {"labels": {"app": name}},
                    "spec": {
                        "containers": [
                            {
                                "name": name,
                                "image": image,
                                "ports": [{"containerPort": 3389, "protocol": "TCP"}],
                                "env": [
                                    {"name": key, "value": value}
                                    for key, value in environment.items()
                                ],
                                "resources": {
                                    "limits": {"cpu": "2", "memory": "6Gi"},
                                    "requests": {"cpu": "0.4", "memory": "1.6Gi"},
                                },
                                "imagePullPolicy": "Always",
                                "volumeMounts": volume_mount,
                            },
                        ],
                        "volumes": volume,
                        "restartPolicy": "Always",
                    },
                },
            },
        }
        return self.v1_apps.create_namespaced_deployment(
            config.KUBERNETES_NAMESPACE, body
        )

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
                                "volumes": [
                                    {
                                        "name": "script",
                                        "configMap": {
                                            name: config.KUBERNETES_RELEASE_NAME
                                            + "-ease-backup",
                                        },
                                    }
                                ],
                                "containers": [
                                    {
                                        "name": name,
                                        "image": image,
                                        "imagePullPolicy": "Always",
                                        "env": [
                                            {"name": key, "value": value}
                                            for key, value in environment.items()
                                        ],
                                        "volumeMounts": [
                                            {
                                                "name": "script",
                                                "mountPath": "/opt/scripts",
                                            }
                                        ],
                                    }
                                ],
                                "restartPolicy": "Never",
                            }
                        }
                    }
                },
            },
        }

        return self.v1_batch.create_namespaced_cron_job(
            namespace=config.KUBERNETES_NAMESPACE, body=body
        )

    def _create_service(
        self, name: str, deployment_name: str
    ) -> kubernetes.client.V1Service:
        body = {
            "kind": "Service",
            "apiVersion": "v1",
            "metadata": {
                "name": name,
            },
            "spec": {
                "ports": [
                    {
                        "name": "rdp",
                        "protocol": "TCP",
                        "port": 3389,
                        "targetPort": 3389,
                    }
                ],
                "selector": {"app": deployment_name},
                "type": "ClusterIP",
            },
        }
        return self.v1_core.create_namespaced_service(config.KUBERNETES_NAMESPACE, body)

    def _create_persistent_volume_claim(self, username):
        body = {
            "apiVersion": "v1",
            "kind": "PersistentVolumeClaim",
            "metadata": {
                "name": self._get_claim_name(username),
            },
            "spec": {
                "accessModes": [config.KUBERNETES_STORAGE_ACCESS_MODE],
                "storageClassName": config.KUBERNETES_STORAGE_CLASS_NAME,
                "resources": {"requests": {"storage": "20Gi"}},
            },
        }
        try:
            self.v1_core.create_namespaced_persistent_volume_claim(
                config.KUBERNETES_NAMESPACE, body
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
        return self.v1_core.read_namespaced_service(id, config.KUBERNETES_NAMESPACE)

    def _delete_deployment(self, id: str) -> kubernetes.client.V1Status:
        try:
            return self.v1_apps.delete_namespaced_deployment(
                id, config.KUBERNETES_NAMESPACE
            )
        except kubernetes.client.exceptions.ApiException:
            log.exception("Error deleting deployment")

    def _delete_cronjob(self, id: str) -> kubernetes.client.V1Status:
        try:
            return self.v1_batch.delete_namespaced_cron_job(
                id, config.KUBERNETES_NAMESPACE
            )
        except kubernetes.client.exceptions.ApiException:
            log.exception("Error deleting cronjob")

    def _delete_service(self, id: str) -> kubernetes.client.V1Status:
        try:
            return self.v1_core.delete_namespaced_service(
                id, config.KUBERNETES_NAMESPACE
            )
        except kubernetes.client.exceptions.ApiException:
            log.exception("Error deleting service")
