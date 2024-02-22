# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


import io

import pytest
import yaml

from capellacollab.config import exceptions as config_exceptions
from capellacollab.config import loader


def test_loader_unique_key_loader_succeeds():
    """Test that loading a YAML file with unique keys succeeds."""
    yaml_str = """
        key1: value1
        key2: value2
        """
    result = yaml.load(yaml_str, Loader=loader.UniqueKeyLoader)
    assert result == {"key1": "value1", "key2": "value2"}


def test_loader_unique_key_loader_fails():
    """Test that attempting to load a YAML file with duplicate keys raises an exception."""
    yaml_str = """
        key1: value1
        key1: value2
    """
    with pytest.raises(config_exceptions.InvalidConfigurationError) as excinfo:
        yaml.load(yaml_str, Loader=loader.UniqueKeyLoader)
    assert "Duplicate key 'key1' found in configuration." in str(excinfo.value)


class MockLocation:
    _exists: bool = False
    content: str | None = "key: value"

    def exists(self):
        return self._exists

    def open(self, encoding: str = "utf-8"):  # pylint: disable=unused-argument
        return io.StringIO(self.content)

    def absolute(self):
        return "mocked_location"


@pytest.fixture(name="mock_locations")
def fixture_mock_locations() -> tuple[MockLocation, MockLocation]:

    mock_location_1 = MockLocation()
    mock_location_2 = MockLocation()
    return mock_location_1, mock_location_2


def test_loader_does_config_exist_true(
    mock_locations: tuple[MockLocation, MockLocation]
):
    """Test that does_config_exist returns True when a config file exists in one of the provided locations."""

    mock_location_1, mock_location_2 = mock_locations
    mock_location_1._exists = False
    mock_location_2._exists = True
    loader.config_locations = [mock_location_1, mock_location_2]

    assert loader.does_config_exist() is True


def test_loader_does_config_exist_false(
    mock_locations: tuple[MockLocation, MockLocation]
):
    """Test that does_config_exist returns False when a config file does not exist in one of the provided locations."""

    mock_location_1, mock_location_2 = mock_locations
    mock_location_1._exists = False
    mock_location_2._exists = False
    loader.config_locations = [mock_location_1, mock_location_2]

    assert loader.does_config_exist() is False


def test_load_yaml_exists(mock_locations: tuple[MockLocation, MockLocation]):
    """Test that load_yaml successfully loads when a config file is in one of the provided locations."""

    mock_location_1, mock_location_2 = mock_locations
    mock_location_1._exists = False
    mock_location_2.content = None
    mock_location_2._exists = True
    mock_location_2.content = "key: value"
    loader.config_locations = [mock_location_1, mock_location_2]

    assert loader.load_yaml() == {"key": "value"}


def test_load_yaml_not_exists(
    mock_locations: tuple[MockLocation, MockLocation]
):
    """Test that load_yaml raises an exception when no config file is found in provided locations."""

    mock_location_1, mock_location_2 = mock_locations
    mock_location_1._exists = False
    mock_location_2._exists = False
    loader.config_locations = [mock_location_1, mock_location_2]

    with pytest.raises(FileNotFoundError):
        loader.load_yaml()
