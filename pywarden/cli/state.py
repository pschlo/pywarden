from pathlib import Path
from dataclasses import dataclass


@dataclass
class CliState:
  cli_path: Path
  session_key: str|None = None
  data_dir: Path|None = None
