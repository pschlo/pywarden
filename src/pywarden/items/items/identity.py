from __future__ import annotations
from typing import TypedDict

from ..item import Item


class IdentityItem(Item):
  identity: IdentityData

class IdentityData(TypedDict):
  title: str
  firstName: str
  middleName: str
  lastName: str
  address1: str
  address2: str
  address3: str
  city: str
  state: str
  postalCode: str