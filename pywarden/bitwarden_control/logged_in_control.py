from __future__ import annotations

from contextlib import contextmanager
from typing import Any
from collections.abc import Iterator
from pywarden.cli import CliControl
from pywarden.api import ApiControl
from .config import ApiConfig
from .unlocked_control import UnlockedControl


class LoggedInControl:
  cli: CliControl
  api: ApiControl

  def __init__(self, cli: CliControl, api: ApiControl) -> None:
    self.cli = cli
    self.api = api

    self.status = self.api.status

  @staticmethod
  def create(cli: CliControl, api_conf: ApiConfig) -> LoggedInControl:
    print(f"Starting API server")
    proc = cli.serve_api(host=api_conf.hostname, port=api_conf.port)
    api = ApiControl.create(proc, host=api_conf.hostname, port=api_conf.port)
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
    except:
      try: self.api.lock
      except Exception as e: print(f"{e.__class__.__name__}: {e}")
      try: self.cli.lock()
      except Exception as e: print(f"{e.__class__.__name__}: {e}")
      raise

    try:
      yield c
    finally:
      c.lock()
