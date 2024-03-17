from __future__ import annotations
from typing import TypedDict, Any

from ..service import Service


type SessionKey = str


class LockUnlockService(Service):
  def lock(self) -> LockResponse:
    resp = self.server.post('/lock')
    return resp.json()

  def unlock(self, password: str) -> UnlockResponse:
    resp = self.server.post('/unlock', json={'password': password})
    return resp.json()


class LockResponse(TypedDict):
  success: bool
  data: Any

class UnlockResponse(TypedDict):
  success: bool
  data: Any
