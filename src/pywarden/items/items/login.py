from __future__ import annotations
from typing import TypedDict

from ..item import Item


class LoginItem(Item):
  login: LoginData


class LoginData(TypedDict):
  uris: list[Uris]
  username: str
  password: str
  totp: str

class Uris(TypedDict):
  match: int
  uri: str