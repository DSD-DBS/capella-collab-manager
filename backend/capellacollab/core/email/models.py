# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import enum

from capellacollab.core import pydantic as core_pydantic


class EMailPriority(enum.Enum):
    LOWEST = 5
    LOW = 4
    NORMAL = 3
    HIGH = 2
    HIGHEST = 1


class EMailContent(core_pydantic.BaseModelStrict):
    subject: str
    message: str
    priority: EMailPriority = EMailPriority.NORMAL
