from __future__ import annotations
from typing import TypedDict, Any

from ..service import Service
from pywarden.items import Item


class AttachmentsService(Service):
  def add_attachment(self, item_id: str, name: str, content: str|bytes) -> Item:
    files = {
      'file': (name, content)
    }
    r = self.conn.post('/attachment', params={'itemid': item_id}, files=files)
    return r.json()['data']

  def get_attachment(self, item_id: str, attachment_id: str) -> bytes:
    r = self.conn.get(f'/object/attachment/{attachment_id}', params={'itemid': item_id})
    return r.content
  
  def delete_attachment(self, item_id: str, attachment_id: str) -> None:
    r = self.conn.delete(f'/object/attachment/{attachment_id}', params={'itemid': item_id})
