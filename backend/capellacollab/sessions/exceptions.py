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


class WorkspaceMountingNotAllowed(core_exceptions.BaseError):
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


class ProvisioningUnsupportedError(core_exceptions.BaseError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            title="Provisioning not supported",
            reason="Provisioning is not supported for persistent sessions.",
            err_code="PROVISIONING_UNSUPPORTED",
        )
