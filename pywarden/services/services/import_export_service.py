from __future__ import annotations
from typing import TypedDict, Any

from pywarden.api import ActiveLocalApiServer

from ..service import LocalService


class ImportExportService(LocalService):
  def get_export(self) -> str:
    return self.cli.get_export()