import logging
import secrets
from base64 import b64decode
from datetime import datetime
from typing import Text, Dict, Union

import websockets

from ocpp.routing import on
from ocpp.v201 import ChargePoint as cp
from ocpp.v201.call_result import (
    BootNotificationPayload,
    StatusNotificationPayload,
)
from ocpp.v201.enums import BootReasonType, ConnectorStatusType, Action, RegistrationStatusType
from ocpp.exceptions import ProtocolError

from ocppdemo.consts import OCP2_0_1
from ocppdemo.errors import AuthorizationException

logging.basicConfig(level=logging.INFO)


def authorise(credentials: Text) -> None:
    username, password = b64decode(credentials).decode().split(":")
    correct_user_name = "user"
    correct_pass = "pass"

    is_correct_username = secrets.compare_digest(username, correct_user_name)
    is_correct_password = secrets.compare_digest(password, correct_pass)
    if not (is_correct_username and is_correct_password):
        raise AuthorizationException()


class CSMS(cp):
    is_powered_up: bool = False

    @on(Action.BootNotification)
    def on_boot_notification(
        self, charging_station: Dict[Text, Text], reason: BootReasonType
    ) -> BootNotificationPayload:

        self.is_powered_up = True

        return BootNotificationPayload(
            current_time=datetime.utcnow().isoformat(),
            interval=10,
            status=RegistrationStatusType.accepted,
        )

    @on(Action.StatusNotification)
    def on_status_notification(
        self,
        connector_id: int,
        timestamp: datetime,
        evse_id: int,
        connector_status: ConnectorStatusType,
    ) -> Union[StatusNotificationPayload, ProtocolError]:

        # Ensuring order of messages, need to make sure CP power up has happened first
        if not self.is_powered_up:
            raise ProtocolError("Charging point has not powered up yet.")

        return StatusNotificationPayload()


async def on_connect(websocket, path):  # type: ignore
    try:
        auth_headers = websocket.request_headers["Authorisation"]
        authorise(credentials=auth_headers.replace("Basic ", ""))
    except KeyError:
        logging.info("No authorisation headers supplied!")
        return await websocket.close()
    except AuthorizationException:
        logging.info("Invalid Username or Password")
        return await websocket.close()

    try:
        requested_protocols = websocket.request_headers["Sec-WebSocket-Protocol"]
    except KeyError:
        logging.info("Client hasn't requested any Subprotocol. " "Closing Connection")
        return await websocket.close()

    if websocket.subprotocol:
        logging.info("Protocols Matched: %s", websocket.subprotocol)
    else:
        logging.warning(
            "Protocols Mismatched | Expected Subprotocols: %s,"
            " but client supports %s | Closing connection",
            websocket.available_subprotocols,
            requested_protocols,
        )
        return await websocket.close()

    charge_point_id = path.strip("/")
    charge_point = CSMS(charge_point_id, websocket)

    await charge_point.start()


async def start_server() -> None:
    server = await websockets.serve(  # type: ignore
        on_connect, "0.0.0.0", 9000, subprotocols=[OCP2_0_1]
    )

    logging.info("CSMS Server now listening to new connections...")
    await server.wait_closed()
