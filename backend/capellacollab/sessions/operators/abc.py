# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import abc
import typing as t
from datetime import datetime


class Operator(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def start_persistent_session(
        cls,
        username: str,
        password: str,
        docker_image: str,
        t4c_license_secret: str | None,
        t4c_json: list[dict[str, str | int]] | None,
    ) -> t.Dict[str, t.Any]:
        """Start / Create a session

        Parameters
        ---------
        username
            Username of the workspace user
        password
            Password for the remote connection
        docker_image:
            The image to start
        repositories
            T4C Repositories that are predefined in the workspace

        Returns
        ------
            Dictionary with Session information.
        """

    @classmethod
    @abc.abstractmethod
    def start_readonly_session(
        self,
        password: str,
        git_url: str,
        git_revision: str,
        entrypoint: str,
        git_username: str,
        git_password: str,
    ) -> t.Dict[str, t.Any]:
        """Start / Create a session

        Parameters
        ---------
        password
            Password for the remote connection
        git_url
            Git URL of the model that should be cloned
        git_branch
            Git Branch of the model that should be cloned

        Returns
        ------
            Dictionary with Session information.
        """

    @classmethod
    @abc.abstractmethod
    def get_session_state(self, id: str) -> str:
        """Get session state

        Paramters
        ---------
        id
            ID of the Session

        Returns
        ------
        state
            State of the current Session
        """

    @classmethod
    @abc.abstractmethod
    def kill_session(self, id: str) -> None:
        """Kill the session

        Paramters
        ---------
        id
            ID of the Session
        """

    @classmethod
    @abc.abstractmethod
    def get_session_logs(self, id: str) -> str:
        """Get session state

        Paramters
        ---------
        id
            ID of the Session

        Returns
        ------
        logs
            Logs of the current session
        """

    @classmethod
    @abc.abstractmethod
    def create_cronjob(
        self, image: str, environment: t.Dict[str, str], schedule="* * * * *"
    ) -> str:
        pass

    @classmethod
    @abc.abstractmethod
    def delete_cronjob(self, id: str) -> None:
        pass

    @classmethod
    @abc.abstractmethod
    def get_cronjob_last_run(self, id: str) -> str:
        pass

    @classmethod
    @abc.abstractmethod
    def get_cronjob_last_state(self, name: str) -> str:
        pass

    @classmethod
    @abc.abstractmethod
    def get_cronjob_last_starting_date(self, name: str) -> datetime | None:
        pass

    @classmethod
    @abc.abstractmethod
    def get_job_logs(self, id: str) -> str:
        pass

    @classmethod
    @abc.abstractmethod
    def trigger_cronjob(self, name: str) -> None:
        pass
