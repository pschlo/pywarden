from __future__ import annotations
from typing import TypedDict, Any

from ..service import Service


class MiscService(Service):
  def sync(self) -> SyncResponse:
    resp = self.conn.post('/sync')
    return resp.json()
  
  def status(self) -> StatusResponse:
    resp = self.conn.get('/status')
    return resp.json()


class SyncResponse(TypedDict):
  success: bool
  data: Any


class StatusResponse(TypedDict):
  success: bool
  data: StatusResponseData

class StatusResponseData(TypedDict):
  object: str
  template: StatusResponseDataTemplate

class StatusResponseDataTemplate(TypedDict):
  serverUrl: str
  lastSync: str
  userEmail: str
  userID: str
  status: str