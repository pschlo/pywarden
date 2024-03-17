from __future__ import annotations
from dataclasses import dataclass
from typing import TypedDict, Any, Generic, TypeVar, cast, TypeGuard, Type

from ..item import Item


class SecureNoteItem(Item):
  secureNote: SecureNoteData


class SecureNoteData(TypedDict):
  type: int