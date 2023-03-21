from base64 import b64encode
from datetime import datetime

from ocpp.v201.enums import ConnectorStatusType, BootReasonType
from ocpp.exceptions import ProtocolError
from ocpp.v201.call_result import (
    BootNotificationPayload,
    StatusNotificationPayload,
)

from ocppdemo.errors import AuthorizationException
from ocppdemo.server import authorise, CSMS

import pytest

client = CSMS(id="CP", connection=None)


def test_authorise_with_wrong_type_raises():
    with pytest.raises(TypeError):
        assert authorise({})


def test_authorise_with_empty_creds_raises():
    with pytest.raises(ValueError):
        assert authorise(b"")


def test_authorise_with_wrong_creds_raises():
    user_pass = f"user_id:wrongPass"
    basic_credentials = b64encode(user_pass.encode()).decode()
    with pytest.raises(AuthorizationException):
        assert authorise(basic_credentials)


def test_authorise_with_valid_creds_passes():
    user_pass = f"user:pass"
    basic_credentials = b64encode(user_pass.encode()).decode()
    assert authorise(basic_credentials) is None


def test_csmc_on_status_request_errors_before_power_up():
    with pytest.raises(ProtocolError):
        assert client.on_status_notification(
            connector_id=1,
            timestamp=datetime.now(),
            evse_id=1,
            connector_status=ConnectorStatusType.available,
        )


def test_csmc_on_boot_request_returns_boot_payload_type():
    assert isinstance(
        client.on_boot_notification(charging_station={}, reason=BootReasonType.power_up),
        BootNotificationPayload,
    )


def test_csmc_on_status_request_after_power_up_passes():
    client_two = CSMS(id="CP2", connection=None)
    client_two.on_boot_notification(charging_station={}, reason=BootReasonType.power_up)
    assert (
        client_two.on_status_notification(
            connector_id=1,
            timestamp=datetime.now(),
            evse_id=1,
            connector_status=ConnectorStatusType.available,
        )
        == StatusNotificationPayload()
    )
