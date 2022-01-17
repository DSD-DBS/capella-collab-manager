import abc
import pathlib
import typing as t
from asyncio import subprocess

from t4cclient.config import (
    KUBERNETES_API_URL,
    KUBERNETES_NAMESPACE,
    KUBERNETES_TOKEN,
    PERSISTENT_IMAGE,
    READONLY_IMAGE,
    T4C_LICENCE,
    T4C_SERVER_HOST,
    T4C_SERVER_PASSWORD,
    T4C_SERVER_PORT,
    config_directory,
)
from t4cclient.core.operators.__main__ import Operator


class KubernetesOperator(Operator):
    values_path = config_directory / "values.yaml"
    helm_args = [
        "--kube-apiserver",
        KUBERNETES_API_URL,
        "--kube-token",
        KUBERNETES_TOKEN,
        "--namespace",
        KUBERNETES_NAMESPACE,
        "-f",
        values_path,
    ]

    kubectl_args = [
        "--token",
        KUBERNETES_TOKEN,
        "--server",
        KUBERNETES_API_URL,
        "--namespace",
        KUBERNETES_NAMESPACE,
    ]

    def __post_init__(self):
        self.args += [
            *self._get_helm_option("t4c.licence", T4C_LICENCE),
            *self._get_helm_option("t4c.host", T4C_SERVER_HOST),
            *self._get_helm_option("t4c.port", T4C_SERVER_PORT),
            *self._get_helm_option("image.readonly", READONLY_IMAGE),
            *self._get_helm_option("image.persistent", PERSISTENT_IMAGE),
        ]

    def start_persistent_session(
        self,
        username: str,
        password: str,
        repositories: t.List[str],
    ) -> t.Dict[str, t.Any]:
        return self._start_session(
            type="persistent",
            username=username,
            password=password,
            repository=repositories,
        )

    def start_readonly_session(
        self, password: str, git_url: str, git_branch: str
    ) -> t.Dict[str, t.Any]:
        pass

    def _start_session(
        self, type: str, username: str, password: str, repository: str
    ) -> t.Dict[str, t.Any]:
        release_name = username + "-" + repository
        subprocess.run(
            [
                "helm",
                "install",
                *self.args,
                *self._get_helm_option("username", username),
                *self._get_helm_option("password", password),
                *self._get_helm_option("repository", repository),
                release_name,
            ],
            cwd=pathlib.Path(__file__).parent / "helm",
        )
        return self.__export_attrs_from_container(release_name)

    def _get_helm_option(self, key: str, value: str) -> t.List[str]:
        return ["--set", key + "=" + value]

    def get_session_state(self, id: str) -> str:
        return "-"

    def kill_session(self, id: str) -> None:
        self.__delete_deployment(id)
        self.__delete_service(id)

    def __export_attrs_from_container(self, release_name):
        url = subprocess.run(
            [
                "kubectl",
                "get",
                *self.kubectl_args,
                "-o",
                'jsonpath="{.status.loadBalancer.ingress[0].hostname}',
                "services",
                release_name + "-service",
            ],
            capture_output=True,
        ).stdout

        creation_timestamp = subprocess.run(
            [
                "kubectl",
                "get",
                *self.kubectl_args,
                "-o",
                'jsonpath="{.metadata.creationTimestamp}',
                "deployments",
                release_name + "-deployment",
            ],
            capture_output=True,
        ).stdout

        return {
            "id": release_name,
            "ports": [3389],
            "created_at": creation_timestamp,
            "mac": "Not implemented yet.",
            "host": url,
        }
