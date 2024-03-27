from __future__ import annotations
from pywarden.cli import CliControl
from pywarden.local_api import LocalApiControl


class UnlockedControl:
  cli: CliControl
  api: LocalApiControl

  def __init__(self, cli: CliControl, api: LocalApiControl) -> None:
    self.cli = cli
    self.api = api

  def get_items(self):
    return self.api.get_items()

  def lock(self) -> None:
    print(f"Locking vault")
    self.api.lock()
