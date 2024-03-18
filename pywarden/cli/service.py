
from .connection import CliConnection


class Service:
  conn: CliConnection

  def __init__(self, conn: CliConnection) -> None:
    self.conn = conn