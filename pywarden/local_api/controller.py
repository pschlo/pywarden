from __future__ import annotations

from pywarden.cli import Cli
from .local_api import LocalApi


"""
Returned by context manager
"""
class Controller:
  api: LocalApi
  cli: Cli

  def __init__(self, api: LocalApi, cli: Cli) -> None:
    self.api = api
    self.cli = cli

  def shutdown(self) -> None:
    print(f"Shutting down Bitwarden Control")
    print(f"  Stopping API")
    self.api.shutdown()
    print(f"  Locking vault")
    self.cli.lock()
    print(f"  Logging out")
    self.cli.logout()
