# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import typing as t

import pydantic


def from_snake_to_camel(name: str) -> str:
    components = name.split("_")
    return components[0] + "".join(
        component.title() for component in components[1:]
    )


class BaseConfig(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(
        extra="forbid",
        alias_generator=from_snake_to_camel,
    )


class DockerConfig(BaseConfig):
    registry: str = pydantic.Field(
        default="k3d-myregistry.localhost:12345/capella/collab",
        description=(
            "The registry from which to pull the Collaboration Manager images, "
            "i.e. the session-preparation image."
        ),
        examples=[
            "ghcr.io/dsd-dbs/capella-collab-manager",
            "k3d-myregistry.localhost:12345/capella/collab",
        ],
    )
    sessions_registry: str = pydantic.Field(
        default="k3d-myregistry.localhost:12345",
        description=(
            "The default registry from which to pull Docker images for session containers. "
            "It is only used during initial tool creation. "
            "After the initial creation, you can change the registry for each tool individually in the UI."
        ),
        examples=["ghcr.io/dsd-dbs/capella-dockerimages"],
    )
    external_registry: str = pydantic.Field(
        default="docker.io",
        description=(
            "The external registry from which to pull Docker images from Docker Hub, "
            "used to enabe Loki monitoring."
        ),
        examples=["docker.io"],
    )

    tag: str = pydantic.Field(
        default="latest",
        description=(
            "Docker tag to use for the Collaboration Manager images, "
            "i.e. the session-preparation image."
        ),
        examples=["main", "v3.1.0", "branch-name"],
    )


class K8sPodSecurityContext(BaseConfig):
    run_as_user: int = pydantic.Field(
        default=1004370000,
        description="The UID under which the Pod's containers will run as non-root.",
        examples=[1004370000],
    )
    run_as_group: int = pydantic.Field(
        default=1004370000,
        description=(
            "The GID under which the Pod's containers will run, "
            "sets all processes of the container to run as this group."
        ),
        examples=[1004370000],
    )
    fs_group: int = pydantic.Field(
        default=1004370000,
        description=(
            "The GID fo rthe volumes that support ownership management, "
            "used when setting the ownership of volume filesystems, "
            "when determining access for volume filesystems, and for other purposes."
        ),
        examples=[1004370000],
    )
    run_as_non_root: bool = True


class K8sClusterConfig(BaseConfig):
    image_pull_policy: t.Literal["Always", "IfNotPresent", "Never"] = (
        pydantic.Field(
            default="Always",
            description=(
                "Determines whether an image should be pulled,"
                "must match one of the examples."
            ),
            examples=["Always", "IfNotPresent", "Never"],
        )
    )
    pod_security_context: K8sPodSecurityContext | None = (
        K8sPodSecurityContext()
    )


class K8sPromtailConfig(BaseConfig):
    loki_enabled: bool = pydantic.Field(
        default=True,
        description="Whether to enable Loki monitoring.",
        examples=[True],
    )
    loki_url: str = pydantic.Field(
        default="http://localhost:30001/loki/api/v1/push",
        alias="lokiURL",
        description="The URL of the Loki instance to which to push logs.",
        examples=["http://localhost:30001/loki/api/v1/push"],
    )
    loki_username: str = pydantic.Field(
        default="localLokiUser",
        description="The username for the Loki instance.",
        examples=["localLokiUser"],
    )
    loki_password: str = pydantic.Field(
        default="localLokiPassword",
        description="The password for the Loki instance.",
        examples=["localLokiPassword"],
    )
    server_port: int = pydantic.Field(
        default=3101,
        description="The port of the promtail server.",
        examples=[3101],
    )


class K8sConfig(BaseConfig):
    storage_class_name: str = pydantic.Field(
        default="local-path",
        description="The name of the StorageClass used for persistent volumes.",
        examples=["local-path"],
    )
    storage_access_mode: t.Literal[
        "ReadWriteOnce", "ReadOnlyMany", "ReadWriteMany", "ReadWriteOncePod"
    ] = pydantic.Field(
        default="ReadWriteOnce",
        description=(
            "The access mode of the StorageClass used for persistent volumes,"
            "must match one of the examples."
        ),
        examples=[
            "ReadWriteOnce",
            "ReadOnlyMany",
            "ReadWriteMany",
            "ReadWriteOncePod",
        ],
    )
    promtail: K8sPromtailConfig = K8sPromtailConfig()
    namespace: str = pydantic.Field(
        default="collab-sessions",
        description="The namespace in which to deploy the session containers.",
        examples=["collab-sessions"],
    )
    cluster: K8sClusterConfig = K8sClusterConfig()
    context: str | None = pydantic.Field(
        default=None,
        description="The name of the Kubernetes context to use.",
        examples=["k3d-collab-cluster"],
    )
    ingress_class_name: str = pydantic.Field(
        default="traefik",
        description="The name of the IngressClass to use.",
        examples=["traefik", "nginx"],
    )


class GeneralConfig(BaseConfig):
    host: str = pydantic.Field(
        default="localhost",
        description="The host name of the application.",
        examples=["localhost", "capella.example.com"],
    )
    port: int | str = pydantic.Field(
        default=8000,
        description="The port the application should run on.",
        examples=[8000, 443, 8080],
    )
    scheme: t.Literal["http", "https"] = pydantic.Field(
        default="http",
        description='The identifier for the protocol to be used, must be "http" or "https"',
        examples=["http", "https"],
    )


class ExtensionGuacamoleConfig(BaseConfig):
    base_uri: str = pydantic.Field(
        default="http://localhost:8080/guacamole",
        alias="baseURI",
        description="The base URI of the Guacamole instance.",
        examples=["http://localhost:8080/guacamole"],
    )
    public_uri: str = pydantic.Field(
        default="http://localhost:8080/guacamole",
        alias="publicURI",
        description="The public URI of the Guacamole instance.",
        examples=["http://localhost:8080/guacamole"],
    )
    username: str = pydantic.Field(
        default="guacadmin",
        description="The username for the Guacamole instance.",
        examples=["guacadmin"],
    )
    password: str = pydantic.Field(
        default="guacadmin",
        description=(
            "The password for the Guacamole instance,"
            "the default should be changed immediately."
        ),
        examples=["guacadmin"],
    )


class ExtensionsConfig(BaseConfig):
    guacamole: ExtensionGuacamoleConfig = ExtensionGuacamoleConfig()


class AuthOauthClientConfig(BaseConfig):
    id: str = pydantic.Field(
        default="default", description="The authentication provider client ID."
    )
    secret: str = pydantic.Field(
        default="", description="The authentication provider client secret."
    )


class AuthOauthEndpointsConfig(BaseConfig):
    authorization: str | None = pydantic.Field(
        default=None,
        description=(
            "The URL of the authorization endpoint. "
            "If not set, the URL is read from the well-known endpoint."
        ),
    )
    well_known: str = pydantic.Field(
        default="http://localhost:8083/default/.well-known/openid-configuration",
        description="The URL of the OpenID Connect discovery document.",
        examples=[
            "http://localhost:8083/default/.well-known/openid-configuration"
        ],
    )


class ClaimMappingConfig(BaseConfig):
    identifier: str = pydantic.Field(default="sub")
    username: str = pydantic.Field(default="sub")
    email: str | None = pydantic.Field(default="email")


class AuthenticationConfig(BaseConfig):
    endpoints: AuthOauthEndpointsConfig = AuthOauthEndpointsConfig()
    audience: str = pydantic.Field(default="default")
    mapping: ClaimMappingConfig = ClaimMappingConfig()
    scopes: list[str] = pydantic.Field(
        default=["openid", "profile", "offline_access"],
        description="List of scopes that application neeeds to access the required attributes.",
    )
    client: AuthOauthClientConfig = AuthOauthClientConfig()
    redirect_uri: str = pydantic.Field(
        default="http://localhost:4200/oauth2/callback",
        description="The URI to which the user is redirected after authentication.",
        examples=["http://localhost:4200/oauth2/callback"],
        alias="redirectURI",
    )


class PipelineConfig(BaseConfig):
    timeout: int = pydantic.Field(
        default=60,
        description="The timeout (in minutes) for pipeline runs.",
        examples=[60, 90],
    )


class DatabaseConfig(BaseConfig):
    url: str = pydantic.Field(
        default="postgresql://dev:dev@localhost:5432/dev",
        description=(
            "The URL of the database. "
            "The format is described here: https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING-URIS"
        ),
        examples=["postgresql://dev:dev@localhost:5432/dev"],
    )


class InitialConfig(BaseConfig):
    admin: str = pydantic.Field(
        default="admin",
        description="The username given to the admin user at database intitialization and for testing.",
        examples=["admin"],
    )


class LoggingConfig(BaseConfig):
    level: t.Literal[
        "CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"
    ] = pydantic.Field(
        default="DEBUG",
        description="The logging level to use across the entire application.",
        examples=["DEBUG", "ERROR"],
    )
    log_path: str = pydantic.Field(
        default="logs/",
        description="The path to the log file (saved as 'backend.log').",
        examples=["logs/"],
    )


class RequestsConfig(BaseConfig):
    timeout: int = pydantic.Field(
        default=2,
        description=(
            "The number (in seconds) to wait for a response from external services."
            "External services are TeamForCapella, Guacamole, Grafana Loki and Prometheus."
        ),
        examples=[2, 5],
    )


class PrometheusConfig(BaseConfig):
    url: str = pydantic.Field(
        default="http://localhost:8080/prometheus/",
        description="The base URL of the Prometheus instance.",
        examples=["http://localhost:8080/prometheus/"],
    )


class AppConfig(BaseConfig):
    docker: DockerConfig = DockerConfig()
    k8s: K8sConfig = K8sConfig(context="k3d-collab-cluster")
    general: GeneralConfig = GeneralConfig()
    extensions: ExtensionsConfig = ExtensionsConfig()
    authentication: AuthenticationConfig = AuthenticationConfig()
    prometheus: PrometheusConfig = PrometheusConfig()
    database: DatabaseConfig = DatabaseConfig()
    initial: InitialConfig = InitialConfig()
    logging: LoggingConfig = LoggingConfig()
    requests: RequestsConfig = RequestsConfig()
    pipelines: PipelineConfig = PipelineConfig()
