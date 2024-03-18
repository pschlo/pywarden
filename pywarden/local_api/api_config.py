from dataclasses import dataclass


@dataclass
class ApiConfig:
  hostname: str = 'localhost'
  port: int = 8087