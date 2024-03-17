from __future__ import annotations
from dataclasses import dataclass
from typing import TypedDict, Any, Generic, TypeVar, cast, TypeGuard, Type

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