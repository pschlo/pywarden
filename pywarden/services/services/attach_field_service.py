from __future__ import annotations
from typing import TypedDict, Any

from ..service import Service


class AttachFieldService(Service):
  def add_attachment(self, item_id: str, name: str, content: str|bytes) -> AddAttachmentResponse:
    files = {
      'file': (name, content)
    }
    resp = self.server.post('/attachment', params={'itemid': item_id}, files=files)
    return resp.json()

  def get_attachment(self, item_id: str, attachment_id: str) -> bytes:
    resp = self.server.get(f'/object/attachment/{attachment_id}', params={'itemid': item_id})
    return resp.content
  
  def delete_attachment(self, item_id: str, attachment_id: str) -> DeleteAttachmentResponse:
    resp = self.server.delete(f'/object/attachment/{attachment_id}', params={'itemid': item_id})
    return resp.json()
    

class AddAttachmentResponse(TypedDict):
  success: bool

class DeleteAttachmentResponse(TypedDict):
  success: bool
