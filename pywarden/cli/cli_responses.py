from typing import Literal, TypedDict, cast


class StatusResponse(TypedDict):
  serverUrl: str|None
  lastSync: str|None
  status: Literal['unauthenticated', 'locked', 'unlocked']

class AuthenticatedStatusResponse(StatusResponse):
  userEmail: str
  userId: str
