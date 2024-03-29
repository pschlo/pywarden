from __future__ import annotations
from pathlib import Path

from pywarden.cli import CliControl
from pywarden.api import ApiControl


class UnlockedBwControl:
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
  @property
  def session_key(self) -> str:
    key = self.cli.session_key
    assert key is not None
    return key
  

  def lock(self) -> None:
    print(f"Locking vault")
    self.api.lock()
    self.cli.lock()
