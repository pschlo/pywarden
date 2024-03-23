from dataclasses import dataclass
from pathlib import Path


@dataclass
class CliConfig:
  cli_path: Path = Path('bw')
  data_dir: Path|None = None
