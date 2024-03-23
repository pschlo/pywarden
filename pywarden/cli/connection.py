from __future__ import annotations
from subprocess import Popen, PIPE, CompletedProcess
from pathlib import Path
from typing import Any, overload, Literal
from collections.abc import Sequence
import os

from .cli_responses import StatusResponse


"""
Low-level communication interface to local Bitwarden CLI
"""
class CliConnection:
  path: Path
  session_key: str|None = None
  data_dir: Path|None = None


  def __init__(self, path: Path) -> None:
    self.path = path

  def get_env(self) -> dict[str,str]:
    env: dict[str,str] = dict()
    
    if self.session_key is not None:
      env['BW_SESSION'] = self.session_key
    if self.data_dir is not None:
      env['BITWARDEN_APPDATA_DIR'] = str(self.data_dir)
    
    return os.environ.copy() | env


  @overload
  def run_command(
    self,
    command: Sequence[str],
    *,
    input: bytes|None = None,
    background: Literal[True],
  ) -> Popen[bytes]: ...
  
  @overload
  def run_command(
    self,
    command: Sequence[str],
    *,
    input: bytes|None = None,
    background: Literal[False] = False,
  ) -> CompletedProcess[bytes]: ...


  def run_command(
    self,
    command: Sequence[str],
    *,
    input: bytes|None = None,
    background: bool = False,
  ) -> Popen[bytes] | CompletedProcess[bytes]:
    
    proc = Popen([str(self.path), *command], stdin=PIPE, stdout=PIPE, stderr=PIPE, env=self.get_env())
    if background:
      return proc
    stdout, stderr = proc.communicate(input)
    return CompletedProcess(proc.args, proc.returncode, stdout=stdout, stderr=stderr)
