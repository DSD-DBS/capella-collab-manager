# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pydantic
import pytest

from capellacollab.tools import models as tools_models


def test_validate_tools():
    with pytest.raises(pydantic.ValidationError):
        tools_models.Resources(
            default_profile=tools_models.DefaultResourceProfile(),
            additional={
                "test1": tools_models.AdditionalResourceProfile(
                    usernames=["test", "test"]
                ),
            },
        )

    with pytest.raises(pydantic.ValidationError):
        tools_models.Resources(
            default_profile=tools_models.DefaultResourceProfile(),
            additional={
                "test1": tools_models.AdditionalResourceProfile(
                    usernames=["test"]
                ),
                "test2": tools_models.AdditionalResourceProfile(
                    usernames=["test"]
                ),
            },
        )


def test_get_profile():
    default_profile = tools_models.DefaultResourceProfile(
        memory=tools_models.MemoryResources(requests="1Gi", limits="2Gi"),
        cpu=tools_models.CPUResources(requests=0.4, limits=2),
    )
    different_profile = tools_models.AdditionalResourceProfile(
        usernames=["testuser"],
        memory=tools_models.MemoryResources(requests="1Gi", limits="2Gi"),
        cpu=tools_models.CPUResources(requests=0.4, limits=2),
    )

    resources = tools_models.Resources(
        default_profile=default_profile,
        additional={
            "test": different_profile,
        },
    )

    resource_profile = resources.get_profile(None)
    assert resource_profile == default_profile

    resource_profile = resources.get_profile("fakeuser")
    assert resource_profile == default_profile

    resource_profile = resources.get_profile("testuser")
    assert resource_profile == different_profile
