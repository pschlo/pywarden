from __future__ import annotations
from subprocess import Popen
import subprocess
import json
from pathlib import Path
from typing import Any, ContextManager, TypedDict, Literal, cast
from collections.abc import Sequence
import time
import requests
import math

from .cli_responses import StatusResponse, AuthenticatedStatusResponse



# wrapper around Bitwarden CLI

class BitwardenCli:
  path: Path
  
  def __init__(self, path: Path = Path('bw')) -> None:
    self.path = path

  def run_cli_command(self, command: Sequence[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run([str(self.path), *command], text=True, capture_output=True)
  
  def get_status(self) -> StatusResponse:
    return json.loads(self.run_cli_command(['status']).stdout)

  def login(self, email: str, password: str) -> None:
    if self.run_cli_command(['login', email, password]).returncode > 0:
      raise RuntimeError(f"Login failed")
    
  def logout(self) -> None:
    if self.run_cli_command(['logout']).returncode > 0:
      raise RuntimeError(f"Logout failed")