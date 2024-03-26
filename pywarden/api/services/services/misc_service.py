from __future__ import annotations
from typing import TypedDict, Any

from pywarden.constants import AuthStatusResponse, DEFAULT_SERVER
from ..service import Service


class MiscService(Service):
  def sync(self) -> SyncResponse:
    resp = self.conn.post('/sync')
    return resp.json()
  
  def status(self) -> AuthStatusResponse:
    r = self.conn.get('/status')
    data = r.json()['data']['template']
    # fix serverUrl of None
    if 'serverUrl' in data and data['serverUrl'] is None:
      data['serverUrl'] = DEFAULT_SERVER
    return data


class SyncResponse(TypedDict):
  success: bool
  data: Any
