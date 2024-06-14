from __future__ import annotations
from typing import TypedDict

from ..item import Item


class SecureNoteItem(Item):
  secureNote: SecureNoteData


class SecureNoteData(TypedDict):
  type: int