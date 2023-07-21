from pydantic import BaseModel as _BaseModel
from pydantic import ConfigDict

__all__ = [
    "BaseModel",
]


class BaseModel(_BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
    )
