# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from capellacollab.core import pydantic as core_pydantic


class EMailContent(core_pydantic.BaseModelStrict):
    subject: str
    message: str
