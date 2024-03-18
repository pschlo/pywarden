from abc import ABC

from ..connection import ApiConnection


"""
Represents a service that can interact with a Bitwarden Vault Management API
"""
class Service(ABC):
  conn: ApiConnection

  def __init__(self, conn: ApiConnection) -> None:
    self.conn = conn
