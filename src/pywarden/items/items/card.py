from __future__ import annotations
from dataclasses import dataclass
from typing import TypedDict, Any, Generic, TypeVar, cast, TypeGuard, Type

from ..item import Item


class CardItem(Item):
  card: CardData


class CardData(TypedDict):
  cardholderName: str
  brand: str
  number: str
  expMonth: str
  expYear: str
  code: str
