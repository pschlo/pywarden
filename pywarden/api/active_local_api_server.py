from __future__ import annotations
from subprocess import Popen
from typing import Any

from .bitwarden_cli import BitwardenCli
from .api_connection import ApiConnection
from .local_api_config import LocalApiConfig


"""
Represents a running instance of a local Bitwarden Vault Management API server.
Things you can do with this object:
  - communicate with the API
  - shut the server down
"""
class ActiveLocalApiServer(ApiConnection):
  process: Popen
  cli: BitwardenCli

  def __init__(self, process: Popen, config: LocalApiConfig, cli: BitwardenCli) -> None:
    super().__init__('http', config.hostname, config.port)
    self.process = process
    self.cli = cli


  def shutdown(self):
    print(f"Shutting down API server")
    print(f"  Locking vault")
    self.cli.lock()
    print(f"  Logging out")
    self.cli.logout()
    print(f"  Terminating process")
    self.process.terminate()
