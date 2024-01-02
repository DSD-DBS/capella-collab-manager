# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import datetime


def datetime_serializer(
    dt: datetime.datetime | None,
) -> datetime.datetime | None:
    if dt:
        return dt.replace(tzinfo=datetime.UTC)
    return None
