# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from fastapi import status

from capellacollab.core import exceptions as core_exceptions
from capellacollab.projects.toolmodels import models as toolmodels_models
from capellacollab.sessions import models as sessions_models
from capellacollab.tools import models as tools_models


class UnsupportedSessionTypeError(core_exceptions.BaseError):
    def __init__(
        self,
        tool: tools_models.DatabaseTool,
        session_type: sessions_models.SessionType,
    ):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            title="Session type unsupported",
            reason=(
                f"The tool {tool.name} doesn't support the session type '{session_type.value}'."
            ),
            err_code="SESSION_TYPE_UNSUPPORTED",
        )


class ConflictingSessionError(core_exceptions.BaseError):
    def __init__(
        self,
        tool: tools_models.DatabaseTool,
        version: tools_models.DatabaseVersion,
    ):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            title="Conflicting session",
            reason=(
                f"You already have a '{tool.name}' session with version '{version.name}'. "
                "Please terminate the existing session or reconnect to it."
            ),
            err_code="EXISTING_SESSION",
        )


class ToolAndModelMismatchError(core_exceptions.BaseError):
    def __init__(
        self,
        version: tools_models.DatabaseVersion,
        model: toolmodels_models.DatabaseToolModel,
    ):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            title="Model version mismatch",
            reason=(
                f"The model '{model.name}' is not compatible with the tool {version.tool.name} ({version.name})'."
            ),
            err_code="MODEL_VERSION_MISMATCH",
        )


class InvalidConnectionMethodIdentifierError(core_exceptions.BaseError):
    def __init__(
        self,
        tool: tools_models.DatabaseTool,
        connection_method_id: str,
    ):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            title="Connection method unknown",
            reason=(
                f"The connection method with identifier '{connection_method_id}' doesn't exist on the tool '{tool.name}'."
            ),
            err_code="CONNECTION_METHOD_UNKNOWN",
        )
