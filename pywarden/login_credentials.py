from __future__ import annotations
from enum import Enum
from typing import TypedDict


class EmailCredentials(TypedDict):
  email: str
  password: str
  two_step_credentials: TwoStepCredentials|None


class TwoStepCredentials(TypedDict):
  type: TwoStepType
  code: str

class TwoStepType(Enum):
  AUTHENTICATOR = 0
  EMAIL = 1
  YUBIKEY = 3
