from __future__ import annotations
from subprocess import Popen
from typing import Any


from pywarden.api import ApiConnection
from pywarden.cli import Cli
from .config import ApiConfig


"""
Represents a running instance of a local Bitwarden Vault Management API server.
Things you can do with this object:
  - communicate with the API
  - shut the server down
"""
class ActiveApiServer(ApiConnection):
  process: Popen
  cli: Cli

  def __init__(self, process: Popen, config: ApiConfig, cli: Cli) -> None:
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
