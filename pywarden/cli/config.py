from dataclasses import dataclass
from pathlib import Path


@dataclass
class CliConfig:
  path: Path = Path('bw')
