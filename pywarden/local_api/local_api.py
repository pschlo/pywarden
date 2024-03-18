from __future__ import annotations
from subprocess import Popen
from typing import Any, override


from pywarden.api import Api, ApiConnection
from pywarden.api.services.services.attachments_service import AttachmentsService
from pywarden.api.services.services.items_service import ItemsService
from pywarden.api.services.services.misc_service import MiscService
from pywarden.cli import Cli
from .api_config import ApiConfig





"""
Represents a running instance of a local Bitwarden Vault Management API server.
Things you can do with this object:
  - communicate with the API
  - shut the server down
"""
class LocalApi(Api):
  process: Popen

  def __init__(self, process: Popen, attachments: AttachmentsService, items: ItemsService, misc: MiscService) -> None:
    super().__init__(attachments, items, misc)
    self.process = process

  @override
  @staticmethod
  def create(conn: ApiConnection, process: Popen) -> LocalApi:
    return LocalApi(
      process=process,
      attachments = AttachmentsService(conn),
      items = ItemsService(conn),
      misc = MiscService(conn)
    )
    

  def shutdown(self):
    self.process.terminate()
