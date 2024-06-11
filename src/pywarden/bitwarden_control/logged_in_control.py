from __future__ import annotations

from contextlib import contextmanager
from typing import Any, overload
from collections.abc import Iterator
import logging

from pywarden.cli import CliControl
from pywarden.api import ApiControl
from .config import ApiConfig
from .unlocked_control import UnlockedBwControl


log = logging.getLogger(__name__)


class LoggedInBwControl:
  cli: CliControl
  api: ApiControl


  @overload
  def __init__(self, cli: CliControl, api: ApiControl): ...
  @overload
  def __init__(self, cli: CliControl, api: ApiConfig): ...
  def __init__(self, cli: CliControl, api: ApiControl|ApiConfig) -> None:
    if isinstance(api, ApiConfig):
      conf = api
      log.info(f"Starting API server")
      proc = cli.serve_api(host=conf.hostname, port=conf.port)
      api = ApiControl.create(proc, host=conf.hostname, port=conf.port)
      api.wait_until_ready(timeout_secs=conf.startup_timeout_secs)
    
    self.cli = cli
    self.api = api
    self.status = self.api.status

  @property
  def data_dir(self):
    return self.cli.data_dir
  @property
  def cli_path(self):
    return self.cli.cli_path
  @property
  def api_hostname(self):
    return self.api.hostname
  @property
  def api_port(self):
    return self.api.port


  def logout(self) -> None:
    log.info(f"Logging out")
    self.cli.logout()

  def stop_api(self) -> None:
    log.info(f"Stopping API server")
    self.api.shutdown()

  @contextmanager
  def unlock(self, password: str) -> Iterator[UnlockedBwControl]:
    log.info(f"Unlocking vault")

    try:
      key = self.api.unlock(password)
      self.cli.session_key = key
      c = UnlockedBwControl(self.cli, self.api)
    except:
      try: self.api.lock()
      except Exception as e: log.error(f"{e.__class__.__name__}: {e}")
      try: self.cli.lock()
      except Exception as e: log.error(f"{e.__class__.__name__}: {e}")
      raise

    try:
      yield c
    finally:
      c.lock()

  @contextmanager
  def as_unlocked(self) -> Iterator[UnlockedBwControl]:
    yield UnlockedBwControl(self.cli, self.api)
