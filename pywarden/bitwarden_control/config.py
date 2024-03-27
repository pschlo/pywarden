from dataclasses import dataclass
from pathlib import Path

from pywarden.cli import DEFAULT_SERVER


@dataclass
class CliConfig:
  # connection settings
  cli_path: Path = Path('bw')
  data_dir: Path|None = None

  # config service settings
  server: str = DEFAULT_SERVER

@dataclass
class ApiConfig:
  hostname: str = 'localhost'
  port: int = 8087
  startup_timeout_secs: float|None = None
