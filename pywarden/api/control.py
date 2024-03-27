from __future__ import annotations
import requests
from subprocess import Popen, TimeoutExpired, CompletedProcess
import time

from .services import AttachmentsService, ItemsService, MiscService, AuthService
from .connection import ApiConnection
from .state import ApiState


class ApiControl:
  process: Popen[bytes]
  state: ApiState

  _attachments: AttachmentsService
  _items: ItemsService
  _misc: MiscService
  _auth: AuthService

  def __init__(self,
    process: Popen,
    state: ApiState,
    attachments_service: AttachmentsService,
    items_service: ItemsService,
    misc_service: MiscService,
    auth_service: AuthService
  ) -> None:
    self.process = process
    self.state = state
    self._attachments = attachments_service
    self._items = items_service
    self._misc = misc_service
    self._auth = auth_service

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
  def create(process: Popen, host: str, port: int) -> ApiControl:
    state = ApiState()
    conn = ApiConnection(state, scheme='http', host=host, port=port)
    return ApiControl(
      process=process,
      state=state,
      attachments_service = AttachmentsService(conn),
      items_service = ItemsService(conn),
      misc_service = MiscService(conn),
      auth_service = AuthService(conn)
    )

  def is_reachable(self) -> bool:
    try:
      self.status()
      return True
    except requests.ConnectionError:
      return False

  def is_alive(self) -> bool:
    return self.process.poll() is None
    
  def shutdown(self, timeout_secs: float|None = None) -> None:
    self.process.terminate()
    try:
      self.process.wait(timeout_secs)
    except TimeoutExpired:
      raise TimeoutError(f"API server did not exit after {timeout_secs} seconds")

  def wait_until_ready(self, timeout_secs: float|None = None):
    t0 = time.perf_counter()

    while timeout_secs is None or time.perf_counter() - t0 < timeout_secs:
      if not self.is_alive():
        _, stderr = self.process.communicate()
        print(stderr)
        raise TimeoutError(f"API server process is dead")
      if self.is_reachable():
        break
      time.sleep(0.1)
    else:
      self.shutdown(timeout_secs)
      raise TimeoutError(f"API server failed to start after {timeout_secs} seconds")
