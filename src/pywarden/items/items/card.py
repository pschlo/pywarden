from __future__ import annotations
from typing import TypedDict

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
