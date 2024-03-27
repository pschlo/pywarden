from __future__ import annotations
from typing import TypedDict, Any

from pywarden.constants import AuthStatusResponse, DEFAULT_SERVER
from ..service import Service


class MiscService(Service):
  def sync(self) -> Any:
    r = self.conn.post('/sync')
    return r.json()['data']
  
  def status(self) -> AuthStatusResponse:
    r = self.conn.get('/status')
    status = r.json()['data']['template']
    # fix serverUrl of None
    if 'serverUrl' in status and status['serverUrl'] is None:
      status['serverUrl'] = DEFAULT_SERVER
    return status
