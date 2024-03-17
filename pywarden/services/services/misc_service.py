from __future__ import annotations
from typing import TypedDict, Any

from ..service import Service


class MiscService(Service):
  def sync(self) -> Any:
    resp = self.server.post('/sync')
    json = resp.json()
    return {
      'success': json['success']
    }
  
  def status(self) -> Any:
    resp = self.server.get('/status')
    return resp.json()
