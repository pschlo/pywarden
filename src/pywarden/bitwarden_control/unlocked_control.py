from __future__ import annotations
from pywarden.cli import CliControl
from pywarden.api import ApiControl


class UnlockedControl:
  cli: CliControl
  api: ApiControl

  def __init__(self, cli: CliControl, api: ApiControl) -> None:
    self.cli = cli
    self.api = api

    self.status = self.api.status
    self.get_items = self.api.get_items
    self.get_item = self.api.get_item
    self.delete_item = self.api.delete_item
    self.get_attachment = self.api.get_attachment
    self.add_attachment = self.api.add_attachment
    self.delete_attachment = self.api.delete_attachment

    self.get_export = self.cli.get_export

  def lock(self) -> None:
    print(f"Locking vault")
    self.api.lock()
    self.cli.lock()
