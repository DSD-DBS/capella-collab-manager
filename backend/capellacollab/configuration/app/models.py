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
            "used to enable Loki monitoring."
        ),
        examples=["docker.io"],
    )
    github_registry: str = pydantic.Field(
        default="ghcr.io",
        description=(
            "The registry pointing to ghcr.io or an alternative mirror, "
            "which contains the same content."
        ),
        examples=["ghcr.io"],
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
    fs_group: int | None = pydantic.Field(
        default=1004370000,
        description=(
            "The GID for the volumes that support ownership management, "
            "used when setting the ownership of volume filesystems, "
            "when determining access for volume filesystems, and for other purposes."
        ),
        examples=[1004370000, None],
    )
    fs_group_change_policy: t.Literal["OnRootMismatch", "Always"] = (
        pydantic.Field(
            default="OnRootMismatch",
            description=(
                "Determines when the fsGroup should be applied to the volume."
                " https://kubernetes.io/docs/tasks/configure-pod-container/security-context/#configure-volume-permission-and-ownership-change-policy-for-pods"
            ),
        )
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
    node_selector: dict[str, str] | None = None


class K8sPromtailConfig(BaseConfig):
    loki_enabled: bool = pydantic.Field(
        default=True,
        description="Whether to enable Loki monitoring.",
        examples=[True],
    )
    loki_url: str | None = pydantic.Field(
        default="http://localhost:30001/loki/api/v1",
        alias="lokiURL",
        description=(
            "The URL of the Loki instance to which to push logs."
            " To access loki from the development environment, run `kubectl port-forward service/dev-loki-gateway 30001:80`."
            " When running in a cluster, use `http://{release_name}-loki-gateway.collab-manager.svc.cluster.local/loki/api/v1`"
        ),
        examples=[
            "http://dev-loki-gateway.collab-manager.svc.cluster.local/loki/api/v1"
        ],
    )
    loki_username: str | None = pydantic.Field(
        default="localLokiUser",
        description="The username for the Loki instance.",
        examples=["localLokiUser"],
    )
    loki_password: str | None = pydantic.Field(
        default="localLokiPassword",
        description="The password for the Loki instance.",
        examples=["localLokiPassword"],
    )
    server_port: int | None = pydantic.Field(
        default=3101,
        description="The port of the promtail server.",
        examples=[3101],
    )

    @pydantic.model_validator(mode="after")
    def check_fields_are_set_if_enabled(self) -> t.Self:
        if self.loki_enabled and not (
            self.loki_url
            and self.loki_username
            and self.loki_password
            and self.server_port
        ):
            raise ValueError(
                "Loki monitoring is enabled, but not all required fields are set."
            )
        return self


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
    management_portal_namespace: str = pydantic.Field(
        default="collab-manager",
        description="The namespace where the management portal is deployed in.",
        examples=["collab-manager"],
    )
    release_name: str = pydantic.Field(
        default="dev",
        description="The release name of the Helm chart",
        examples=["dev", "prod", "test123"],
    )


class GeneralConfig(BaseConfig):
    host: str = pydantic.Field(
        default="localhost",
        description="The host name of the application.",
        examples=["localhost", "capella.example.com"],
    )
    port: int | str = pydantic.Field(
        default=4200,
        description="The port the application should run on.",
        examples=[8000, 443, 8080],
    )
    scheme: t.Literal["http", "https"] = pydantic.Field(
        default="http",
        description='The identifier for the protocol to be used, must be "http" or "https"',
        examples=["http", "https"],
    )


class ExtensionGuacamoleConfig(BaseConfig):
    enabled: bool = pydantic.Field(
        default=True, description="Whether to enable Guacamole."
    )
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
    mapping: ClaimMappingConfig = ClaimMappingConfig()
    scopes: list[str] = pydantic.Field(
        default=["openid", "profile", "offline_access"],
        description="List of scopes that the application needs to access the required attributes.",
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
    scheduler: bool = pydantic.Field(
        default=True,
        description=(
            "Whether to enable the integrated pipeline scheduler."
            " IMPORTANT: Only works with exactly one backend replica."
            " When having more replicas, disable this option and run one replica of the scheduler via the CCM CLI."
        ),
    )


class SessionsConfig(BaseConfig):
    timeout: int = pydantic.Field(
        default=90,
        description="The timeout (in minutes) for unused and idle sessions.",
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


class ValkeyConfig(BaseConfig):
    url: str = pydantic.Field(
        default="valkey://default:password@localhost:6379/0"
    )


class InitialConfig(BaseConfig):
    admin: str = pydantic.Field(
        default="admin",
        description="The username given to the admin user at database initialization and for testing.",
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
    profiling: bool = pydantic.Field(
        default=False,
        description="Enable profiling of requests.",
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


class SMTPConfig(BaseConfig):
    enabled: bool = pydantic.Field(
        default=True,
        description="Whether to enable SMTP. Necessary for feedback.",
        examples=[True, False],
    )
    host: str = pydantic.Field(
        description="The SMTP server host.",
        default="localhost:587",
        examples=["smtp.example.com:587"],
        pattern=r"^(.*):(\d+)$",
    )
    user: str = pydantic.Field(
        default="username",
        description="The SMTP server user.",
        examples=["username"],
    )
    password: str = pydantic.Field(
        default="password",
        description="The SMTP server password.",
        examples=["password"],
    )
    sender: str = pydantic.Field(
        default="capella@example.com",
        description="The sender email address.",
        examples=["capella@example.com"],
    )


class AppConfig(BaseConfig):
    docker: DockerConfig = DockerConfig()
    k8s: K8sConfig = K8sConfig(context="k3d-collab-cluster")
    general: GeneralConfig = GeneralConfig()
    extensions: ExtensionsConfig = ExtensionsConfig()
    authentication: AuthenticationConfig = AuthenticationConfig()
    prometheus: PrometheusConfig = PrometheusConfig()
    database: DatabaseConfig = DatabaseConfig()
    valkey: ValkeyConfig = ValkeyConfig()
    initial: InitialConfig = InitialConfig()
    logging: LoggingConfig = LoggingConfig()
    requests: RequestsConfig = RequestsConfig()
    pipelines: PipelineConfig = PipelineConfig()
    sessions: SessionsConfig = SessionsConfig()
    smtp: SMTPConfig | None = SMTPConfig()
