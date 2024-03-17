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
class BitwardenCli:
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

  def login(self, email: str, password: str) -> None:
    if self.run_cli_command(['login', email, password]).returncode > 0:
      raise RuntimeError(f"Login failed")
    self.is_logged_in = True
    
  def logout(self) -> None:
    if self.run_cli_command(['logout']).returncode > 0:
      raise RuntimeError(f"Logout failed")
    self.is_logged_in = False
    
  def lock(self) -> None:
    r = self.run_cli_command(['lock'])
    if r.returncode > 0:
      raise RuntimeError(f"Lock failed")
    self.session_key = None

  def unlock(self, password: str) -> None:
    if not password:
      raise RuntimeError(f"Empty master password")
    r = self.run_cli_command(['unlock', '--raw', password])
    if r.returncode > 0:
      raise RuntimeError(f"Unlock failed")
    self.session_key = r.stdout
    
  def get_export(self) -> str:
    res = self.run_cli_command(['export', '--format', 'json', '--raw'])
    if res.returncode > 0:
      raise RuntimeError(f"Export failed")
    return res.stdout
