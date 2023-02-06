# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import inspect
import typing as t


def get_source_of_python_function(function: t.Callable):
    source = inspect.getsource(function).splitlines()
    leading_whitespaces_to_remove = len(source[1]) - len(source[1].lstrip())

    return "\n".join(
        [line[leading_whitespaces_to_remove:] for line in source[1:]]
    )
