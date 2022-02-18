import abc
import typing as t

from t4cclient.schemas.sessions import WorkspaceType


class Operator(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def start_persistent_session(
        self,
        username: str,
        password: str,
        repositories: t.List[str],
    ) -> t.Dict[str, t.Any]:
        """Start / Create a session

        Parameters
        ---------
        username
            Username of the workspace user
        password
            Password for the remote connection
        repositories
            T4C Repositories that are predefined in the workspace

        Returns
        ------
            Dictionary with Session information.
        """

    @classmethod
    @abc.abstractmethod
    def start_readonly_session(
        self, password: str, git_url: str, git_revision: str, entrypoint: str
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
