from __future__ import annotations
from dataclasses import dataclass
from typing import TypedDict, Any

from pywarden.items import Item
from ..service import Service


class ItemsService(Service):
  def getAll(self) -> GetAllResponse:
    resp = self.api.get('/list/object/items')
    json = resp.json()

    if json['success']:
      items = json['data']['data']
      for item in items:
        fix_item(item)

    return json

  def deleteItem(self, id: str) -> DeleteItemResponse:
    resp = self.api.delete(f'/object/item/{id}')
    return resp.json()
  
  def getItem(self, id: str) -> GetItemResponse:
    resp = self.api.get(f'/object/item/{id}')
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
