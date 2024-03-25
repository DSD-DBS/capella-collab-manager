# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from fastapi import status

from capellacollab.core import exceptions as core_exceptions


class T4CInstanceIsArchivedError(core_exceptions.BaseError):
    def __init__(self, t4c_instance_id: int):
        self.t4c_instance_id = t4c_instance_id
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            title="T4C instance is archived",
            reason=f"The T4C instance identified by {t4c_instance_id} is archived, thus prohibiting the execution of the requested operation.",
            err_code="T4C_INSTANCE_IS_ARCHIVED",
        )


class T4CInstanceWithNameAlreadyExistsError(
    core_exceptions.ResourceAlreadyExistsError
):
    def __init__(self):
        super().__init__(resource_name="T4C Instance", identifier_name="name")
