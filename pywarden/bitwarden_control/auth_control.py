from __future__ import annotations

from contextlib import contextmanager
from typing import Any
from collections.abc import Iterator
from pywarden.cli import CliControl
from pywarden.local_api import LocalApiControl
from .local_api_config import ApiConfig


class LoggedInControl:
  cli: CliControl
  api: LocalApiControl

  def __init__(self, cli: CliControl, api: LocalApiControl) -> None:
    self.cli = cli
    self.api = api

  @staticmethod
  def create(cli: CliControl, api_conf: ApiConfig) -> LoggedInControl:
    print(f"Starting API server")
    proc = cli.serve_api(host=api_conf.hostname, port=api_conf.port)
    api = LocalApiControl.create(proc, host=api_conf.hostname, port=api_conf.port)
    api.wait_until_ready(timeout_secs=api_conf.startup_timeout_secs)
    return LoggedInControl(cli, api)

  def logout(self) -> None:
    print(f"Logging out")
    self.cli.logout()

  def stop_api(self) -> None:
    print(f"Stopping API server")
    self.api.shutdown()

  @contextmanager
  def unlock(self, password: str) -> Iterator[UnlockedControl]:
    print(f"Unlocking vault")
    try:
      key = self.api.unlock(password)
      self.cli.session_key = key
      c = UnlockedControl(self.cli, self.api)
      yield c
    finally:
      c.lock()





class UnlockedControl(LoggedInControl):
  def get_items(self):
    return self.api.get_items()
  
  def lock(self) -> None:
    print(f"Locking vault")
    self.api.lock()
