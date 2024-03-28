from pathlib import Path
from dataclasses import dataclass


@dataclass
class ApiState:
  host: str
  port: int
  scheme: str = 'http'
