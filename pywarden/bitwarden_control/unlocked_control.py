from __future__ import annotations
from pywarden.cli import CliControl
from pywarden.api import ApiControl


class UnlockedControl:
  cli: CliControl
  api: ApiControl

  def __init__(self, cli: CliControl, api: ApiControl) -> None:
    self.cli = cli
    self.api = api

  def get_items(self):
    return self.api.get_items()

  def lock(self) -> None:
    print(f"Locking vault")
    self.api.lock()
