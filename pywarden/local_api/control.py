from __future__ import annotations
from subprocess import Popen, TimeoutExpired
from typing import Any, override
import time


from pywarden.api import ApiControl, ApiConnection, AttachmentsService, ItemsService, MiscService


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
  

  def shutdown(self, timeout_secs: float|None = None) -> None:
    self.process.terminate()

    if timeout_secs is None:
      self.process.wait()
      return
    
    try:
      self.process.wait(timeout_secs)
    except TimeoutExpired:
      raise TimeoutError(f"API server did not exit after {timeout_secs} seconds")


  def wait_until_ready(self, timeout_secs: float|None = None):
    t0 = time.perf_counter()

    if timeout_secs is None:
      while not self.is_reachable():
        time.sleep(0.1)
      return

    while time.perf_counter() - t0 < timeout_secs:
      if self.is_reachable():
        break
      time.sleep(0.1)
    else:
      raise TimeoutError(f"API server failed to start after {timeout_secs} seconds")
