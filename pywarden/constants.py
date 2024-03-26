from __future__ import annotations
from typing import Any, Literal, TypedDict


class StatusResponse(TypedDict):
  serverUrl: str|None
  lastSync: str|None
  status: Literal['unauthenticated', 'locked', 'unlocked']

class AuthStatusResponse(StatusResponse):
  userEmail: str
  userId: str


DEFAULT_SERVER = 'https://bitwarden.com'
