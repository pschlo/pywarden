from __future__ import annotations
from typing import TypeVar, TypeGuard, Type

from .items import LoginItem, SecureNoteItem, CardItem, IdentityItem, SshKeyItem
from .item import Item


T = TypeVar("T", bound=Item)


GET_ITEM_TYPE: dict[int, Type[Item]] = {
    1: LoginItem,
    2: SecureNoteItem,
    3: CardItem,
    4: IdentityItem,
    5: SshKeyItem,
}


def get_item_type(item: Item) -> Type[Item]:
    return GET_ITEM_TYPE[item["type"]]


def is_item_type(item: Item, typ: Type[T]) -> TypeGuard[T]:
    return get_item_type(item) is typ
