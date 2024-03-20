from __future__ import annotations
from subprocess import Popen
import subprocess
from pathlib import Path
from typing import Any
from collections.abc import Sequence


"""
Low-level communication interface to local Bitwarden CLI
"""
class CliConnection:
  path: Path

  def __init__(self, path: Path = Path('bw')) -> None:
    self.path = path

  def run_cli_command(self, command: Sequence[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run([str(self.path), *command], text=True, capture_output=True)
  
  def run_background_command(self, command: Sequence[str]) -> Popen:
    return Popen([str(self.path), *command])
