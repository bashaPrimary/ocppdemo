from dataclasses import dataclass
from typing import Text, Optional

from ocpp.v201.enums import ConnectorStatusType


@dataclass
class Connector:
    id: int
    status: ConnectorStatusType
    meta_data: Optional[Text] = None
