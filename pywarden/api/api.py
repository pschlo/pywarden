from __future__ import annotations
import requests

from .services import AttachmentsService, ItemsService, MiscService
from .connection import ApiConnection


class Api:
  def __init__(self,
    attachments: AttachmentsService,
    items: ItemsService,
    misc: MiscService
  ) -> None:
    self._attachments = attachments
    self._items = items
    self._misc = misc

    # method shortcuts
    self.add_attachment = self._attachments.add_attachment
    self.get_attachment = self._attachments.get_attachment
    self.delete_attachment = self._attachments.delete_attachment

    self.get_items = self._items.getAll
    self.get_item = self._items.getItem
    self.delete_item = self._items.deleteItem

    self.status = self._misc.status
    self.sync = self._misc.sync


  @staticmethod
  def create(conn: ApiConnection) -> Api:
    return Api(
      attachments = AttachmentsService(conn),
      items = ItemsService(conn),
      misc = MiscService(conn)
    )
  
  def is_reachable(self) -> bool:
    try:
      self.status()
      return True
    except requests.ConnectionError:
      return False
