from abc import ABC

from ..api import ActiveApiServer


class Service(ABC):
  server: ActiveApiServer

  def __init__(self, server: ActiveApiServer) -> None:
    self.server = server
