# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import pathlib
import re

import dateutil.parser
import fastapi
import requests
import sqlalchemy.orm

import t4cclient.extensions.backups.jenkins as crud_jenkins
import t4cclient.extensions.modelsources.git.crud as crud_git_models
import t4cclient.extensions.modelsources.git.models as database_git_models
from t4cclient.config import config

cfg = config["backups"]["jenkins"]
JENKINS_AUTH = (cfg["username"], cfg["password"])


def load_pipeline_config(git_model: database_git_models.DB_GitModel):
    MAP_CONFIG_ENV_TO_CONFIG = {
        "T4C_PROJECT_NAME": git_model.project.name,
        "T4C_REPO_NAME": git_model.repository_name,
        "MODEL_ENTRYPOINT": git_model.entrypoint,
        "GIT_BRANCH": git_model.revision,
        "GIT_CREDENTIAL_ID": cfg["git"]["credentialID"],
        "GIT_USERNAME": git_model.username,
        "GIT_EMAIL": cfg["git"]["email"],
        "GIT_MODEL_URL": git_model.path,
        "JENKINS_SCRIPT_REPO_URL": cfg["git"]["scriptRepoURL"],
        "GIT_URL_WITH_CREDENTIALS_ENV": git_model.path.replace("//", "//$USER:$PASS@"),
    }
    filecontent = (pathlib.Path(__file__).parent / "config.xml").read_text()
    pattern = r"__([A-Z0-9]*(?:_[A-Z0-9]+)*)__"
    for match in re.findall(pattern, filecontent):
        filecontent = filecontent.replace(
            f"__{match}__", MAP_CONFIG_ENV_TO_CONFIG[match]
        )
    return filecontent


def post_pipelines_to_jenkins(filecontent: str, pipeline_name: str):
    res = requests.post(
        cfg["baseURL"] + "/createItem?name=" + pipeline_name,
        data=filecontent,
        auth=JENKINS_AUTH,
        headers={
            "Content-Type": "text/xml",
        },
        timeout=config["requests"]["timeout"],
    )
    res.raise_for_status()


def create_pipeline(
    db: sqlalchemy.orm.Session, repository_name: str, git_model_id: int
):
    git_model = crud_git_models.get_model_by_id(db, repository_name, git_model_id)

    filecontent = load_pipeline_config(git_model)
    post_pipelines_to_jenkins(filecontent, "backup-job-" + str(git_model_id))


def get_pipeline(db: sqlalchemy.orm.Session, pipeline_name: str):
    res = requests.get(
        cfg["baseURL"]
        + "/blue/rest/organizations/jenkins/pipelines/"
        + pipeline_name
        + "/runs",
        auth=JENKINS_AUTH,
        timeout=config["requests"]["timeout"],
    )
    if res.status_code == 404:
        crud_jenkins.remove_pipeline_by_name(db, pipeline_name)
        raise fastapi.HTTPException(
            status_code=401,
            detail="The pipeline existed in our system, but not at the Jenkins instance. "
            + "This can happen if Jenkins Pipelines are deleted manually. "
            + "Our database has been updated.",
        )
    res.raise_for_status()

    try:
        latest_pipeline = res.json()[0]
        return {
            "id": latest_pipeline["id"],
            "start_time": dateutil.parser.isoparse(
                latest_pipeline["startTime"]
            ).strftime("%Y-%m-%d %H:%M"),
            "result": latest_pipeline["result"],
            "logs_url": cfg["baseURL"]
            + "/job/"
            + pipeline_name
            + "/"
            + latest_pipeline["id"]
            + "/console",
        }
    except IndexError:
        return None


def trigger_job_run(pipeline_name: str):
    requests.post(
        cfg["baseURL"] + "/job/" + pipeline_name + "/build?delay=0sec",
        auth=JENKINS_AUTH,
        timeout=config["requests"]["timeout"],
    ).raise_for_status()


def remove_pipeline(pipeline_name: str):
    requests.post(
        cfg["baseURL"] + "/job/" + pipeline_name + "/doDelete",
        auth=JENKINS_AUTH,
        timeout=config["requests"]["timeout"],
    ).raise_for_status()
