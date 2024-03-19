from pywarden.api import Service
from pywarden.cli import CliControl

from ..control import ActiveApiServer



"""
Represents a service that can:
  - interact with a Bitwarden Vault Management API
  - use the local Bitwarden CLI
"""
class LocalService(Service):
  cli: CliControl

  def __init__(self, api: ActiveApiServer) -> None:
    super().__init__(api)
    self.cli = api.cli