from __future__ import annotations
from subprocess import Popen, PIPE, CompletedProcess, CalledProcessError
from pathlib import Path
from typing import Any, overload, Literal
from collections.abc import Sequence
import os

from .cli_responses import StatusResponse
from .state import CliState


"""
Low-level communication interface to local Bitwarden CLI
"""
class CliConnection:
  state: CliState


  def __init__(self, state: CliState) -> None:
    self.state = state


  def get_env(self) -> dict[str,str]:
    env: dict[str,str] = dict()

    if self.state.session_key is not None:
      env['BW_SESSION'] = self.state.session_key
    if self.state.data_dir is not None:
      env['BITWARDENCLI_APPDATA_DIR'] = str(self.state.data_dir)
    
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
    
    proc = Popen([str(self.state.cli_path), *command], stdin=PIPE, stdout=PIPE, stderr=PIPE, env=self.get_env())
    if background:
      return proc
    stdout, stderr = proc.communicate(input)
    r = CompletedProcess(proc.args, proc.returncode, stdout=stdout, stderr=stderr)

    try:
      r.check_returncode()
    except CalledProcessError:
      msg = r.stderr.decode().splitlines()[-1]  # only consider last line. Previous lines are sometimes leftover from input prompt.
      print(f"ERROR: {msg}")
      raise

    return r
