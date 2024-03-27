from abc import ABC

from ..connection import ApiConnection


class Service(ABC):
  conn: ApiConnection

  def __init__(self, conn: ApiConnection) -> None:
    self.conn = conn
