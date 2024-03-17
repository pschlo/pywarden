from __future__ import annotations
from dataclasses import dataclass
from typing import TypedDict, Any, Generic, TypeVar, cast, TypeGuard, Type

from pywarden.items import Item, is_item_type, LoginItem, CardItem, SecureNoteItem, IdentityItem
from ..service import Service


class ItemsService(Service):
  def getAll(self) -> GetAllResponse:
    resp = self.server.get('/list/object/items')
    json = resp.json()
    return {
      'success': json['success'],
      'items': json['data']['data']
    }

  def deleteItem(self, id: str) -> DeleteItemResponse:
    resp = self.server.delete(f'/object/item/{id}')
    return resp.json()
  
  def getItem(self, id: str) -> GetItemResponse:
    resp = self.server.get(f'/object/item/{id}')
    return resp.json()



class GetAllResponse(TypedDict):
  success: bool
  items: list[Item]

class DeleteItemResponse(TypedDict):
  success: bool

class GetItemResponse(TypedDict):
  success: bool
  data: Item
  revisionDate: str
  deleteDate: str|None
