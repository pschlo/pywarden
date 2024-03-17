from __future__ import annotations
from dataclasses import dataclass
from typing import TypedDict, Any, Generic, TypeVar, cast, TypeGuard, Type

from pywarden.items import Item, is_item_type, LoginItem, CardItem, SecureNoteItem, IdentityItem
from ..service import Service


class ItemsService(Service):
  def getAll(self) -> GetAllResponse:
    resp = self.server.get('/list/object/items')
    json = resp.json()

    if json['success']:
      items = json['data']['data']
      for item in items:
        fix_item(item)

    return json

  def deleteItem(self, id: str) -> DeleteItemResponse:
    resp = self.server.delete(f'/object/item/{id}')
    return resp.json()
  
  def getItem(self, id: str) -> GetItemResponse:
    resp = self.server.get(f'/object/item/{id}')
    json = resp.json()

    if json['success']:
      item = json['data']
      fix_item(item)

    return json
  

def fix_item(item):
  # ensure that attachments key is always set
  if 'attachments' not in item:
    item['attachments'] = []


class GetAllResponse(TypedDict):
  success: bool
  data: GetAllResponseData

class GetAllResponseData(TypedDict):
  object: str
  data: list[Item]

class DeleteItemResponse(TypedDict):
  success: bool

class GetItemResponse(TypedDict):
  success: bool
  data: Item
  revisionDate: str
  deleteDate: str|None
