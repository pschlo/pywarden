from __future__ import annotations
from subprocess import Popen
from typing import Any, override
import time


from pywarden.api import ApiControl, ApiConnection
from pywarden.api.services.services.attachments_service import AttachmentsService
from pywarden.api.services.services.items_service import ItemsService
from pywarden.api.services.services.misc_service import MiscService



"""
Represents a running instance of a local Bitwarden Vault Management API server.
Things you can do with this object:
  - communicate with the API
  - shut the server down
"""
class LocalApiControl(ApiControl):
  process: Popen

  def __init__(self, process: Popen, attachments: AttachmentsService, items: ItemsService, misc: MiscService) -> None:
    super().__init__(attachments, items, misc)
    self.process = process

  @override
  @staticmethod
  def create(conn: ApiConnection, process: Popen) -> LocalApiControl:
    return LocalApiControl(
      process=process,
      attachments = AttachmentsService(conn),
      items = ItemsService(conn),
      misc = MiscService(conn)
    )
  

  def shutdown(self):
    self.process.terminate()


  def wait_until_ready(self, timeout_secs: float):
    t0 = time.perf_counter()
    
    while time.perf_counter() - t0 < timeout_secs:
      if self.is_reachable():
        break
      time.sleep(0.1)
    else:
      raise TimeoutError(f"API server failed to start after {timeout_secs} seconds")
