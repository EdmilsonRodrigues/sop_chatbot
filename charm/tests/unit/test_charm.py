# Copyright 2024 familia
# See LICENSE file for licensing details.
#
# Learn more about testing at: https://juju.is/docs/sdk/testing

import ops
import ops.testing
import pytest

from charm import SopChatbotBackendCharm


@pytest.fixture
def harness():
    harness = ops.testing.Harness(SopChatbotBackendCharm)
    harness.begin()
    yield harness
    harness.cleanup()


def test_httpbin_pebble_ready(harness: ops.testing.Harness[SopChatbotBackendCharm]):
    # Expected plan after Pebble ready with default config
    expected_plan = {
        "services": {
            "httpbin": {
                "override": "replace",
                "summary": "httpbin",
                "command": "gunicorn -b 0.0.0.0:80 httpbin:app -k gevent",
                "startup": "enabled",
                "environment": {"GUNICORN_CMD_ARGS": "--log-level info"},
            }
        },
    }
    # Simulate the container coming up and emission of pebble-ready event
    harness.container_pebble_ready("httpbin")
    # Get the plan now we've run PebbleReady
    updated_plan = harness.get_container_pebble_plan("httpbin").to_dict()
    # Check we've got the plan we expected
    assert expected_plan == updated_plan
    # Check the service was started
    service = harness.model.unit.get_container("httpbin").get_service("httpbin")
    assert service.is_running()
    # Ensure we set an ActiveStatus with no message
    assert harness.model.unit.status == ops.ActiveStatus()


def test_config_changed_valid_can_connect(harness: ops.testing.Harness[SopChatbotBackendCharm]):
    # Ensure the simulated Pebble API is reachable
    harness.set_can_connect("httpbin", True)
    # Trigger a config-changed event with an updated value
    harness.update_config({"log-level": "debug"})
    # Get the plan now we've run PebbleReady
    updated_plan = harness.get_container_pebble_plan("httpbin").to_dict()
    updated_env = updated_plan["services"]["httpbin"]["environment"]
    # Check the config change was effective
    assert updated_env == {"GUNICORN_CMD_ARGS": "--log-level debug"}
    assert harness.model.unit.status == ops.ActiveStatus()


def test_config_changed_valid_cannot_connect(harness: ops.testing.Harness[SopChatbotBackendCharm]):
    # Trigger a config-changed event with an updated value
    harness.update_config({"log-level": "debug"})
    # Check the charm is in WaitingStatus
    assert isinstance(harness.model.unit.status, ops.WaitingStatus)


def test_config_changed_invalid(harness: ops.testing.Harness[SopChatbotBackendCharm]):
    # Ensure the simulated Pebble API is reachable
    harness.set_can_connect("httpbin", True)
    # Trigger a config-changed event with an updated value
    harness.update_config({"log-level": "foobar"})
    # Check the charm is in BlockedStatus
    assert isinstance(harness.model.unit.status, ops.BlockedStatus)
