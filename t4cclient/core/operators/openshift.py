# TODO: Rework Kubernetes Integration

# import abc
# import typing as t

# import kubernetes
# import kubernetes.client
# import kubernetes.config
# from t4cclient.config import (
#     DOCKER_T4C_CLIENT_IMAGE,
#     KUBERNETES_API_URL,
#     KUBERNETES_NAMESPACE,
#     KUBERNETES_TOKEN,
# )
# from t4cclient.core.operators.__main__ import Operator

# kubernetes.config.load_kube_config_from_dict(
#     {
#         "apiVersion": "v1",
#         "kind": "Config",
#         "clusters": [
#             {
#                 "cluster": {
#                     "insecure-skip-tls-verify": True,
#                     "server": KUBERNETES_API_URL,
#                 },
#                 "name": "db",
#             }
#         ],
#         "contexts": [{"context": {"cluster": "db", "user": "tokenuser"}, "name": "db"}],
#         "current-context": "db",
#         "users": [
#             {
#                 "name": "tokenuser",
#                 "user": {"token": KUBERNETES_TOKEN},
#             }
#         ],
#     }
# )


# class KubernetesOperator(Operator):
#     def __init__(self):
#         self.v1_core = kubernetes.client.CoreV1Api()
#         self.v1_apps = kubernetes.client.AppsV1Api()

#     def start_session(
#         self, username: str, password: str, repository: str
#     ) -> t.Dict[str, t.Any]:
#         deployment = self.__create_deployment(username, password, repository)
#         self.__create_service(username, repository)
#         service = self.__get_service((username + "-" + repository).lower())
#         return self.__export_attrs(deployment, service)

#     def get_session_state(self, id: str) -> str:
#         return "-"

#     def kill_session(self, id: str) -> None:
#         self.__delete_deployment(id)
#         self.__delete_service(id)

#     def __create_deployment(
#         self, username: str, password: str, repository: str
#     ) -> kubernetes.client.V1Deployment:
#         unique_name = (username + "-" + repository).lower()
#         body = {
#             "kind": "Deployment",
#             "apiVersion": "apps/v1",
#             "metadata": {"name": unique_name},
#             "spec": {
#                 "replicas": 1,
#                 "selector": {"matchLabels": {"app": unique_name}},
#                 "template": {
#                     "metadata": {"labels": {"app": unique_name}},
#                     "spec": {
#                         "containers": [
#                             {
#                                 "name": unique_name,
#                                 "image": DOCKER_T4C_CLIENT_IMAGE,
#                                 "ports": [{"containerPort": 3389, "protocol": "TCP"}],
#                                 "env": [
#                                     {"name": "RMT_USERNAME", "value": username},
#                                     {"name": "RMT_PASSWORD", "value": password},
#                                     {"name": "T4C_REPOSITORY", "value": repository},
#                                 ],
#                                 "resources": {
#                                     "limits": {"cpu": "2", "memory": "2Gi"},
#                                     "requests": {"cpu": "1", "memory": "1Gi"},
#                                 },
#                                 "imagePullPolicy": "Always",
#                             },
#                         ],
#                         "restartPolicy": "Always",
#                     },
#                 },
#             },
#         }
#         return self.v1_apps.create_namespaced_deployment(KUBERNETES_NAMESPACE, body)

#     def __create_service(
#         self, username: str, repository: str
#     ) -> kubernetes.client.V1Service:
#         unique_name = (username + "-" + repository).lower()
#         body = {
#             "kind": "Service",
#             "apiVersion": "v1",
#             "metadata": {
#                 "name": unique_name,
#                 "annotations": {
#                     "service.beta.kubernetes.io/aws-load-balancer-connection-idle-timeout": "30",
#                     "service.beta.kubernetes.io/aws-load-balancer-internal": "true",
#                 },
#             },
#             "spec": {
#                 "ports": [
#                     {
#                         "name": "3389-tcp",
#                         "protocol": "TCP",
#                         "port": 3389,
#                         "targetPort": 3389,
#                     }
#                 ],
#                 "selector": {"app": unique_name},
#                 "type": "LoadBalancer",
#             },
#         }
#         return self.v1_core.create_namespaced_service(KUBERNETES_NAMESPACE, body)

#     def __get_service(self, id: str):
#         return self.v1_core.read_namespaced_service(id, KUBERNETES_NAMESPACE)

#     def __delete_deployment(self, id: str) -> kubernetes.client.V1Status:
#         return self.v1_apps.delete_namespaced_deployment(id, KUBERNETES_NAMESPACE)

#     def __delete_service(self, id: str) -> kubernetes.client.V1Status:
#         return self.v1_core.delete_namespaced_service(id, KUBERNETES_NAMESPACE)

#     def __export_attrs(
#         self,
#         deployment: kubernetes.client.V1Deployment,
#         service: kubernetes.client.V1Service,
#     ) -> t.Dict[str, t.Any]:
#         return {
#             "id": deployment.to_dict()["metadata"]["name"],
#             "ports": set([3389]),
#             "created_at": deployment.to_dict()["metadata"]["creation_timestamp"],
#             "mac": "-",
#             "host": service.to_dict()["status"]["load_balancer"]["ingress"]
#             # [0]["hostname"],
#         }
