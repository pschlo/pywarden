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
import os

from .cli_responses import StatusResponse, AuthenticatedStatusResponse


"""
Wrapper around Bitwarden CLI.
Keeps track of logged in/out and vault locked/unlocked state.
"""
class CliConnection:
  path: Path
  _session_key: str | None = None
  is_logged_in: bool

  @property
  def is_locked(self):
    return self._session_key is None
  
  @property
  def session_key(self) -> str|None:
    return self._session_key
  
  @session_key.setter
  def session_key(self, value: str|None) -> None:
    self._session_key = value
    if value is None:
      os.environ.pop('BW_SESSION', None)
    else:
      os.environ['BW_SESSION'] = value


  def __init__(self, path: Path = Path('bw')) -> None:
    self.path = path

    status = self.get_status()['status']
    assert status != 'unlocked'  # cannot possibly be unlocked without session key
    self.is_logged_in = False if status == 'unauthenticated' else True

  def run_cli_command(self, command: Sequence[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run([str(self.path), *command], text=True, capture_output=True)
  
  def run_background_command(self, command: Sequence[str]) -> Popen:
    return Popen([str(self.path), *command])

  def get_status(self) -> StatusResponse:
    return json.loads(self.run_cli_command(['status']).stdout)
