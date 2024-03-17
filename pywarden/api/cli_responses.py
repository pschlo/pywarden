from typing import Literal, TypedDict


class StatusResponse(TypedDict):
  serverUrl: str|None
  lastSync: str|None
  status: Literal['unauthenticated', 'locked', 'unlocked']

class AuthenticatedStatusResponse(StatusResponse):
  status: Literal['locked', 'unlocked']
  userEmail: str
  userId: str