import logging
import random
import string
import typing as t

import kubernetes
import kubernetes.client
import kubernetes.config
from t4cclient import config
from t4cclient.core.operators.abc import Operator

log = logging.getLogger(__name__)

try:
    kubernetes.config.load_incluster_config()
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
        self, password: str, git_url: str, git_branch: str
    ) -> t.Dict[str, t.Any]:
        id = self._generate_id()
        deployment = self._create_deployment(
            config.READONLY_IMAGE,
            id,
            {
                "GIT_USERNAME": config.GIT_USERNAME,
                "GIT_PASSWORD": config.GIT_PASSWORD,
                "GIT_REPO_URL": git_url,
                "GIT_REPO_BRANCH": git_branch,
            },
        )
        self._create_service(id, id)
        service = self._get_service(id)
        return self._export_attrs(deployment, service)

    def get_session_state(self, id: str) -> str:
        return "-"

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
        volume_mount = {}
        volume = {}

        if volume_claim_name:
            volume_mount = {"name": "workspace", "mountPath": "/workspace"}

            volume = {
                "name": "workspace",
                "persistentVolumeClaim": {"claimName": volume_claim_name},
            }

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
                                    "limits": {"cpu": "2", "memory": "2Gi"},
                                    "requests": {"cpu": "1", "memory": "1Gi"},
                                },
                                "imagePullPolicy": "Always",
                                "volumeMounts": [volume_mount],
                            },
                        ],
                        "volumes": [volume],
                        "restartPolicy": "Always",
                    },
                },
            },
        }
        return self.v1_apps.create_namespaced_deployment(
            config.KUBERNETES_NAMESPACE, body
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
                "accessModes": ["ReadWriteMany"],
                "storageClassName": "persistent-sessions-csi",
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
        except kubernetes.client.exceptions.ApiException as e:
            log.exception("Error deleting service")

    def _delete_service(self, id: str) -> kubernetes.client.V1Status:
        try:
            return self.v1_core.delete_namespaced_service(
                id, config.KUBERNETES_NAMESPACE
            )
        except kubernetes.client.exceptions.ApiException as e:
            log.exception("Error deleting service")
