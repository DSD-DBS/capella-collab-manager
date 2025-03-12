# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from fastapi import status

from capellacollab.core import exceptions as core_exceptions
from capellacollab.sessions import models as sessions_models


class SessionNotFoundError(core_exceptions.BaseError):
    def __init__(self, session_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            title="Session not found",
            reason=f"The session with id {session_id} was not found.",
            err_code="SESSION_NOT_FOUND",
        )

    @classmethod
    def openapi_example(cls) -> "SessionNotFoundError":
        return cls("qhrhipmlyjawgtwqlijdtwpbm")


class SessionNotOwnedError(core_exceptions.BaseError):
    def __init__(self, session_id: str):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            title="Session not owned",
            reason=(
                f"The session with id {session_id} does not belong to your user. "
                "Only administrators can manage other sessions!"
            ),
            err_code="SESSION_NOT_OWNED",
        )

    @classmethod
    def openapi_example(cls) -> "SessionNotOwnedError":
        return cls("qhrhipmlyjawgtwqlijdtwpbm")


class SessionAlreadySharedError(core_exceptions.BaseError):
    def __init__(self, username: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            title="Session already shared with user",
            reason=(f"The session is already shared with user '{username}'. "),
            err_code="SESSION_ALREADY_SHARED",
        )

    @classmethod
    def openapi_example(cls) -> "SessionAlreadySharedError":
        return cls("johndoe")


class SessionForbiddenError(core_exceptions.BaseError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            title="Access to sessions of other users forbidden",
            reason=(
                "You can only see your own sessions. "
                "If you are administrator, please use the /sessions endpoint to see all active sessions."
            ),
            err_code="SESSION_FORBIDDEN",
        )

    @classmethod
    def openapi_example(cls) -> "SessionForbiddenError":
        return cls()


class UnsupportedSessionTypeError(core_exceptions.BaseError):
    def __init__(
        self,
        tool_name: str,
        session_type: sessions_models.SessionType,
    ):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            title="Session type unsupported",
            reason=(
                f"The tool {tool_name} doesn't support the session type '{session_type.value}'."
            ),
            err_code="SESSION_TYPE_UNSUPPORTED",
        )

    @classmethod
    def openapi_example(cls) -> "UnsupportedSessionTypeError":
        return cls("Capella", sessions_models.SessionType.PERSISTENT)


class SessionSharingNotSupportedError(core_exceptions.BaseError):
    def __init__(self, tool_name: str, connection_method_name: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            title="Session sharing not supported",
            reason=(
                f"The connection method '{connection_method_name}' of tool '{tool_name}' doesn't support session sharing.'."
            ),
            err_code="SESSION_SHARING_UNSUPPORTED",
        )

    @classmethod
    def openapi_example(cls) -> "SessionSharingNotSupportedError":
        return cls("Capella", "Xpra")


class ConflictingSessionError(core_exceptions.BaseError):
    def __init__(
        self,
        tool_name: str,
        version_name: str,
    ):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            title="Conflicting session",
            reason=(
                f"You already have a '{tool_name}' session with version '{version_name}'. "
                "Please terminate the existing session or reconnect to it."
            ),
            err_code="EXISTING_SESSION",
        )

    @classmethod
    def openapi_example(cls) -> "ConflictingSessionError":
        return cls("Capella", "7.0.0")


class ToolAndModelMismatchError(core_exceptions.BaseError):
    def __init__(
        self,
        tool_name: str,
        version_name: str,
        model_name: str,
    ):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            title="Model version mismatch",
            reason=(
                f"The model '{model_name}' is not compatible with the tool {tool_name} ({version_name})'."
            ),
            err_code="MODEL_VERSION_MISMATCH",
        )

    @classmethod
    def openapi_example(cls) -> "ToolAndModelMismatchError":
        return cls("Capella", "7.0.0", "coffee-machine")


class ProjectAndModelMismatchError(core_exceptions.BaseError):
    def __init__(
        self,
        project_slug: str,
        model_name: str,
    ):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            title="Mismatch between project scope and provisioning",
            reason=(
                f"The model '{model_name}' doesn't belong to the project '{project_slug}'."
            ),
            err_code="MODEL_PROJECT_MISMATCH",
        )

    @classmethod
    def openapi_example(cls) -> "ProjectAndModelMismatchError":
        return cls("coffee-machine", "Coffee Machine")


class InvalidConnectionMethodIdentifierError(core_exceptions.BaseError):
    def __init__(
        self,
        tool_name: str,
        connection_method_id: str,
    ):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            title="Connection method unknown",
            reason=(
                f"The connection method with identifier '{connection_method_id}' doesn't exist on the tool '{tool_name}'."
            ),
            err_code="CONNECTION_METHOD_UNKNOWN",
        )

    @classmethod
    def openapi_example(cls) -> "InvalidConnectionMethodIdentifierError":
        return cls("Capella", "7.0.0")


class WorkspaceMountingNotAllowedError(core_exceptions.BaseError):
    def __init__(
        self,
        tool_name: str,
    ):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            title="Tool doesn't support workspace mounting",
            reason=(
                f"The tool '{tool_name}' doesn't support workspace mounting."
            ),
            err_code="WORKSPACE_MOUNTING_NOT_ALLOWED",
        )

    @classmethod
    def openapi_example(cls) -> "WorkspaceMountingNotAllowedError":
        return cls("Capella")


class TooManyModelsRequestedToProvisionError(core_exceptions.BaseError):
    def __init__(self, max_number_of_models: int):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            title="Too many models requested",
            reason=(
                f"The selected tool only supports up to {max_number_of_models} provisioned model(s) per session."
            ),
            err_code="TOO_MANY_MODELS_REQUESTED",
        )

    @classmethod
    def openapi_example(cls) -> "TooManyModelsRequestedToProvisionError":
        return cls(2)


class ProvisioningUnsupportedError(core_exceptions.BaseError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            title="Provisioning not supported",
            reason="Provisioning is not supported for persistent sessions.",
            err_code="PROVISIONING_UNSUPPORTED",
        )

    @classmethod
    def openapi_example(cls) -> "ProvisioningUnsupportedError":
        return cls()


class ProvisioningRequiredError(core_exceptions.BaseError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            title="Provisioning is required for this tool",
            reason="Provisioning is required for persistent sessions of the selected tool.",
            err_code="PROVISIONING_REQUIRED",
        )

    @classmethod
    def openapi_example(cls) -> "ProvisioningRequiredError":
        return cls()


class ProjectScopeRequiredError(core_exceptions.BaseError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            title="A project scope is required.",
            reason="Persistent provisioning requires a project scope.",
            err_code="PROJECT_SCOPE_REQUIRED",
        )

    @classmethod
    def openapi_example(cls) -> "ProjectScopeRequiredError":
        return cls()


class GuacamoleDisabledError(core_exceptions.BaseError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            title="Can't spawn Guacamole session",
            reason="Guacamole is not enabled for this instance. Ask your administrator for support.",
            err_code="GUACAMOLE_DISABLED",
        )

    @classmethod
    def openapi_example(cls) -> "GuacamoleDisabledError":
        return cls()
