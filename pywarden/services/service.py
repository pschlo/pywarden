from abc import ABC

from ..api import ApiConnection, ActiveLocalApiServer, BitwardenCli


"""
Represents a service that can interact with a Bitwarden Vault Management API
"""
class Service(ABC):
  api: ApiConnection

  def __init__(self, api: ApiConnection) -> None:
    self.api = api

"""
Represents a service that can:
  - interact with a Bitwarden Vault Management API
  - use the local Bitwarden CLI
"""
class LocalService(Service):
  cli: BitwardenCli

  def __init__(self, api: ActiveLocalApiServer) -> None:
    super().__init__(api)
    self.cli = api.cli
