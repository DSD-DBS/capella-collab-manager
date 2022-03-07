import configparser
import logging
import os
import pathlib

config_parser = configparser.RawConfigParser()
config_directory = pathlib.Path(__file__).parents[1] / "config"
config_file_path = config_directory / "config.ini"
config_parser.read(config_file_path)

log = logging.getLogger(__name__)


def get_config(group: str, key: str, fallback: str = "") -> str:
    config = config_parser.get(
        group, key, fallback=os.environ.get(f"{group}_{key.upper()}", fallback)
    )

    if not config:
        log.warning(
            "Configuration %s of group %s not found. Defaulting to empty string.",
            key,
            group,
        )

    return config


PERSISTENT_IMAGE = get_config("DOCKER", "PERSISTENT_IMAGE")
READONLY_IMAGE = get_config("DOCKER", "READONLY_IMAGE")
EASE_IMAGE = get_config("DOCKER", "EASE_IMAGE")
WORKSPACE_MOUNT_VOLUME = get_config("DOCKER", "WORKSPACE_MOUNT_VOLUME")
DOCKER_PORT_RANGE = get_config("DOCKER", "PORT_RANGE")
DOCKER_HOST = get_config("DOCKER", "CONTAINER_HOST")

GUACAMOLE_URI = get_config("GUACAMOLE", "BASE_URI")
GUACAMOLE_PUBLIC_URI = get_config("GUACAMOLE", "PUBLIC_URI")
GUACAMOLE_USERNAME = get_config("GUACAMOLE", "USERNAME")
GUACAMOLE_PASSWORD = get_config("GUACAMOLE", "PASSWORD")

OAUTH_TOKEN_ENDPOINT = get_config("OAUTH", "token_issuance_endpoint")
OAUTH_ENDPOINT = get_config("OAUTH", "authorization_endpoint")
OAUTH_CLIENT_ID = get_config("OAUTH", "client_id")
OAUTH_CLIENT_SECRET = get_config("OAUTH", "client_secret")
OAUTH_REDIRECT_URI = get_config("OAUTH", "redirect_uri")
USERNAME_CLAIM = get_config("OAUTH", "USERNAME_CLAIM")
DATABASE_URL = get_config("SQL", "DATABASE_URL")

T4C_SERVER_USERNAME = get_config("T4C_SERVER", "USERNAME")
T4C_SERVER_PASSWORD = get_config("T4C_SERVER", "PASSWORD")
T4C_SERVER_HOST = get_config("T4C_SERVER", "HOST")
T4C_SERVER_PORT = get_config("T4C_SERVER", "PORT")
T4C_LICENCE = get_config("T4C_SERVER", "LICENCE")

T4C_USAGE_API = get_config("T4C_SERVER", "USAGE_API")
T4C_REST_API = get_config("T4C_SERVER", "REST_API")

KUBERNETES_CONTEXT = get_config("KUBERNETES", "CONTEXT", "default")
KUBERNETES_NAMESPACE = get_config("KUBERNETES", "NAMESPACE")
KUBERNETES_STORAGE_CLASS_NAME = get_config(
    "KUBERNETES", "STORAGE_CLASS_NAME", "persistent-sessions-csi"
)
KUBERNETES_STORAGE_ACCESS_MODE = get_config(
    "KUBERNETES", "STORAGE_ACCESS_MODE", "ReadWriteMany"
)
KUBERNETES_TOKEN = get_config("KUBERNETES", "NAMESPACE")
KUBERNETES_API_URL = get_config("KUBERNETES", "API_URL")
KUBERNETES_RELEASE_NAME = get_config("KUBERNETES", "RELEASE_NAME")
OPERATOR_TYPE = get_config("OPERATOR", "TYPE")

JENKINS_BASE_URL = get_config("JENKINS", "BASE_URL")
JENKINS_USERNAME = get_config("JENKINS", "USERNAME")
JENKINS_PASSWORD = get_config("JENKINS", "PASSWORD")

JENKINS_GIT_USERNAME = get_config("JENKINS_GIT", "USERNAME")
JENKINS_GIT_EMAIL = get_config("JENKINS_GIT", "EMAIL")
JENKINS_GIT_CREDENTIAL_ID = get_config("JENKINS_GIT", "CREDENTIAL_ID")
JENKINS_GIT_SCRIPT_REPO_URL = get_config("JENKINS_GIT", "SCRIPT_REPO_URL")

GIT_USERNAME = get_config("GIT", "USERNAME")
GIT_PASSWORD = get_config("GIT", "PASSWORD")

INITIAL_ADMIN_USER = get_config("USERS", "INITIAL_ADMIN")

REQUESTS_TIMEOUT = 0.5
LOGGING_LEVEL = get_config("LOGGING", "LEVEL", "DEBUG")
