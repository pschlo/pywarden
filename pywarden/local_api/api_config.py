from dataclasses import dataclass


@dataclass
class ApiConfig:
  hostname: str = 'localhost'
  port: int = 8087
  startup_timeout_secs: float = 10
