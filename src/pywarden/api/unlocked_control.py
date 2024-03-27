from __future__ import annotations
from typing import Any
from .control import ApiControl


class UnlockedApiControl:
  api: ApiControl

  def __init__(self) -> None:
    pass

  def get_items(self) -> list[Any]: ...
