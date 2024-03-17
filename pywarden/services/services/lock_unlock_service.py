from __future__ import annotations
from typing import TypedDict

from ..service import Service


type SessionKey = str


class LockUnlockService(Service):
  def lock(self) -> LockResponse:
    resp = self.server.post('/lock')
    json = resp.json()
    return {
      'success': json['success']
    }

  def unlock(self, password: str) -> UnlockResponse:
    resp = self.server.post('/unlock', json={'password': password})
    json = resp.json()
    return {
      'success': json['success'],
      'session_key': json['data']['raw']
    }
    

class LockResponse(TypedDict):
  success: bool

class UnlockResponse(TypedDict):
  success: bool
  session_key: SessionKey
