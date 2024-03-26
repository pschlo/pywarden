from __future__ import annotations
import requests

from .services import AttachmentsService, ItemsService, MiscService, AuthService
from .connection import ApiConnection
from .state import ApiState


class ApiControl:
  def __init__(self,
    state: ApiState,
    attachments: AttachmentsService,
    items: ItemsService,
    misc: MiscService,
    auth: AuthService
  ) -> None:
    self.state = state
    self._attachments = attachments
    self._items = items
    self._misc = misc
    self._auth = auth

    # method shortcuts
    self.add_attachment = self._attachments.add_attachment
    self.get_attachment = self._attachments.get_attachment
    self.delete_attachment = self._attachments.delete_attachment

    self.get_items = self._items.getAll
    self.get_item = self._items.getItem
    self.delete_item = self._items.deleteItem

    self.status = self._misc.status
    self.sync = self._misc.sync

    self.lock = self._auth.lock
    self.unlock = self._auth.unlock


  @staticmethod
  def create(scheme: str, host: str, port: int) -> ApiControl:
    state = ApiState()
    conn = ApiConnection(state, scheme=scheme, host=host, port=port)
    return ApiControl(
      state=state,
      attachments = AttachmentsService(conn),
      items = ItemsService(conn),
      misc = MiscService(conn),
      auth = AuthService(conn)
    )
  
  def is_reachable(self) -> bool:
    try:
      self.status()
      return True
    except requests.ConnectionError:
      return False
