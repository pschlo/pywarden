from __future__ import annotations
from typing import TypedDict, Any

from ..service import Service


class AuthService(Service):
  def lock(self):
    self.conn.post('/lock')

  # returns the session key
  def unlock(self, password: str) -> str:
    r = self.conn.post('/unlock', json={'password': password})
    return r.json()['data']['raw']
