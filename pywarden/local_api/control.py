from __future__ import annotations
from subprocess import Popen, TimeoutExpired, CompletedProcess
from typing import Any, override
import time


from pywarden.api import ApiControl, ApiConnection, ApiState, AttachmentsService, ItemsService, MiscService, AuthService


class LocalApiControl(ApiControl):
  process: Popen[bytes]

  def __init__(self, process: Popen, state: ApiState, attachments: AttachmentsService, items: ItemsService, misc: MiscService, auth: AuthService) -> None:
    super().__init__(state, attachments, items, misc, auth)
    self.process = process

  @override
  @staticmethod
  def create(process: Popen, host: str, port: int) -> LocalApiControl:
    state = ApiState()
    conn = ApiConnection(state, scheme='http', host=host, port=port)
    return LocalApiControl(
      process=process,
      state=state,
      attachments = AttachmentsService(conn),
      items = ItemsService(conn),
      misc = MiscService(conn),
      auth = AuthService(conn)
    )
  

  def shutdown(self, timeout_secs: float|None = None) -> None:
    self.process.terminate()
    try:
      self.process.wait(timeout_secs)
    except TimeoutExpired:
      raise TimeoutError(f"API server did not exit after {timeout_secs} seconds")
    
  def is_alive(self) -> bool:
    return self.process.poll() is None


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
      raise TimeoutError(f"API server failed to start after {timeout_secs} seconds")
