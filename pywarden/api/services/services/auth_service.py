from __future__ import annotations
from typing import TypedDict, Any

from ..service import Service


class AuthService(Service):
  def lock(self):
    self.conn.post('/lock')

  def unlock(self, password: str) -> Any:
    r = self.conn.post('/unlock', json={'password': password})
    return r.json()