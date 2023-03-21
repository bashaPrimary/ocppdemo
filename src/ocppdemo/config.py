from typing import Text

from pydantic.main import BaseModel


class RequiredEnviron(BaseModel):
    """Represents all required environment variables
    and is used for automatic parsing/validation."""

    CSMS_URL: Text
    CSMS_PORT: Text
    CP_USER: Text
    CP_PASS: Text
