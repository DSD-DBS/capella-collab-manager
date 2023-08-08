# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import datetime


def datetime_serializer(dt: datetime.datetime) -> datetime.datetime:
    return dt.replace(tzinfo=datetime.UTC)
