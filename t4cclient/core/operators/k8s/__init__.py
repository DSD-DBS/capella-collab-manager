import abc
import pathlib
import random
import re
import string
import typing as t
import uuid
from asyncio import subprocess

import kubernetes
import kubernetes.client
import kubernetes.config
from t4cclient import config
from t4cclient.core.operators.__main__ import Operator

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

    def start_persistent_session(
        self,
        username: str,
        password: str,
        repositories: t.List[str],
    ) -> t.Dict[str, t.Any]:
        id = self.__generate_id()
        deployment = self.__create_deployment(
            config.PERSISTENT_IMAGE,
            id,
            {
                "T4C_LICENCE_SECRET": config.T4C_LICENCE,
                "T4C_SERVER_HOST": config.T4C_SERVER_HOST,
                "T4C_SERVER_PORT": config.T4C_SERVER_PORT,
                "T4C_REPOSITORIES": ",".join(repositories),
                "RMT_PASSWORD": password,
            },
        )
        self.__create_service(id, id)
        service = self.__get_service(id)
        return self.__export_attrs(deployment, service)

    def start_readonly_session(
        self, password: str, git_url: str, git_branch: str
    ) -> t.Dict[str, t.Any]:
        id = self.__generate_id()
        deployment = self.__create_deployment(
            config.READONLY_IMAGE,
            id,
            {
                "GIT_USERNAME": config.GIT_USERNAME,
                "GIT_PASSWORD": config.GIT_PASSWORD,
                "GIT_REPO_URL": git_url,
                "GIT_REPO_BRANCH": git_branch,
            },
        )
        self.__create_service(id, id)
        service = self.__get_service(id)
        return self.__export_attrs(deployment, service)

    def get_session_state(self, id: str) -> str:
        return "-"

    def __generate_id(self):
        return "".join(random.choices(string.ascii_lowercase, k=25))

    def kill_session(self, id: str) -> None:
        self.__delete_deployment(id)
        self.__delete_service(id)

    def __export_attrs(
        self,
        deployment: kubernetes.client.V1Deployment,
        service: kubernetes.client.V1Service,
    ) -> t.Dict[str, t.Any]:
        return {
            "id": deployment.to_dict()["metadata"]["name"],
            "ports": set([3389]),
            "created_at": deployment.to_dict()["metadata"]["creation_timestamp"],
            "mac": "-",
            "host": id,
        }

    def __create_deployment(
        self, image: str, name: str, environment: t.Dict
    ) -> kubernetes.client.V1Deployment:
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
                            },
                        ],
                        "restartPolicy": "Always",
                    },
                },
            },
        }
        return self.v1_apps.create_namespaced_deployment(
            config.KUBERNETES_NAMESPACE, body
        )

    def __create_service(
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
                        "name": "3389-tcp",
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

    def __get_service(self, id: str):
        return self.v1_core.read_namespaced_service(id, config.KUBERNETES_NAMESPACE)

    def __delete_deployment(self, id: str) -> kubernetes.client.V1Status:
        return self.v1_apps.delete_namespaced_deployment(
            id, config.KUBERNETES_NAMESPACE
        )

    def __delete_service(self, id: str) -> kubernetes.client.V1Status:
        return self.v1_core.delete_namespaced_service(id, config.KUBERNETES_NAMESPACE)
