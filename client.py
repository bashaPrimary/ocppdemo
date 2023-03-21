import asyncio
import logging
import os
from base64 import b64encode
from datetime import datetime
from typing import Text

import websockets
import dotenv

from ocpp.v201 import ChargePoint
from ocpp.v201.call import BootNotificationPayload, StatusNotificationPayload
from ocpp.v201.enums import ConnectorStatusType, BootReasonType
from ocpp.exceptions import ProtocolError

from ocppdemo.consts import OCP2_0_1
from ocppdemo.datatypes import Connector
from ocppdemo.config import RequiredEnviron

logging.basicConfig(level=logging.INFO)


def basic_auth_header(username, password):
    assert ":" not in username
    user_pass = f"{username}:{password}"
    basic_credentials = b64encode(user_pass.encode()).decode()
    return "Authorisation", f"Basic {basic_credentials}"


async def connect(*,
                  charging_station_id: Text,
                  sub_protocol: Text,
                  model: Text,
                  vendor: Text,
                  env: RequiredEnviron):
    endpoint = env.CSMS_URL
    port = env.CSMS_PORT

    url = f"{endpoint}:{port}/{charging_station_id}"
    async with websockets.connect(
        url,
        subprotocols=[sub_protocol],
        extra_headers=[basic_auth_header(env.CP_USER, env.CP_PASS)],
    ) as ws:
        cs = ChargePointClient(charging_station_id, ws, model, vendor)

        # Idea is connectors get used up and status change to "occupied" (this is not implemented)
        next_connector = next(
            (c for _, c in cs.connectors.items() if c.status == ConnectorStatusType.available),
            None,
        )

        # 0 is for the main connector
        connector_id = next_connector.id if next_connector else 0

        await asyncio.gather(
            cs.start(),
            cs.send_boot_notification(),
            cs.send_status_notification(connector_id=connector_id),
        )


class ChargePointClient(ChargePoint):
    model: Text
    vendor: Text
    connectors = {}
    evse_id = 1

    def __init__(self, id, connection, model, vendor):
        super().__init__(id, connection)
        self.model = model
        self.vendor = vendor

        #  initialise connectors inside this Charging point
        for i in range(1, 10):
            self.connectors[i] = Connector(id=i, status=ConnectorStatusType.available)

    async def send_boot_notification(self):
        request = BootNotificationPayload(
            charging_station={"model": self.model, "vendorName": self.vendor},
            reason=BootReasonType.power_up,
        )
        logging.info(f"(Charging Station) {self.id=} : {request=}")
        response = await self.call(request)
        logging.info(f"(Charging Station) {self.id=} : {response=}")

    async def send_status_notification(self, connector_id: int):
        try:
            request = StatusNotificationPayload(
                connector_id=connector_id,
                timestamp=datetime.utcnow().isoformat(),
                evse_id=self.evse_id,
                connector_status=ConnectorStatusType.available,
            )

            await self.call(request, suppress=False)
        except ProtocolError as e:
            logging.error(e)


async def main(env: RequiredEnviron):
    await asyncio.gather(
        connect(charging_station_id="CP_1", sub_protocol=OCP2_0_1, env=env,
                model="Trek", vendor="Edison"),
        connect(charging_station_id="CP_2", sub_protocol=OCP2_0_1, env=env,
                model="Drive", vendor="Through"),
    )


if __name__ == "__main__":
    dotenv.load_dotenv()
    env = RequiredEnviron.parse_obj(os.environ)
    asyncio.run(main(env))
