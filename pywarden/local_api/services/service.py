from pywarden.api import Service
from pywarden.cli import Cli

from ..local_api import ActiveApiServer



"""
Represents a service that can:
  - interact with a Bitwarden Vault Management API
  - use the local Bitwarden CLI
"""
class LocalService(Service):
  cli: Cli

  def __init__(self, api: ActiveApiServer) -> None:
    super().__init__(api)
    self.cli = api.cli