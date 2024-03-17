from dataclasses import dataclass


@dataclass
class LocalApiConfig:
  hostname: str = 'localhost'
  port: int = 8087