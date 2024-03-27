from __future__ import annotations
from dataclasses import dataclass
from typing import TypedDict, Any, Generic, TypeVar, cast, TypeGuard, Type

from .items import LoginItem, SecureNoteItem, CardItem, IdentityItem
from .item import Item


T = TypeVar('T', bound=Item)


GET_ITEM_TYPE: dict[int, Type[Item]] = {
  1: LoginItem,
  2: SecureNoteItem,
  3: CardItem,
  4: IdentityItem
}


def get_item_type(item: Item) -> Type[Item]:
  return GET_ITEM_TYPE[item['type']]

def is_item_type(item: Item, typ: Type[T]) -> TypeGuard[T]:
  return get_item_type(item) is typ
