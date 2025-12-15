from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class BaseSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")


class LienPosition(str, Enum):
    first = "first"
    second = "second"
    unsecured = "unsecured"
    unknown = "unknown"
