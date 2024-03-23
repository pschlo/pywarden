from dataclasses import dataclass
from pathlib import Path


@dataclass
class CliConfig:
  # connection settings
  cli_path: Path = Path('bw')
  data_dir: Path|None = None

  # config service settings
  server: str|None = None
