from __future__ import annotations
from subprocess import Popen, PIPE, CompletedProcess, CalledProcessError
import logging
from typing import Any, overload, Literal
from collections.abc import Sequence
import os

from .state import CliState


log = logging.getLogger(__name__)


"""
Low-level communication interface to local Bitwarden CLI
"""
class CliConnection:
  state: CliState


  def __init__(self, state: CliState) -> None:
    self.state = state


  def get_env(self) -> dict[str,str]:
    env: dict[str,str] = os.environ.copy()
    if self.state.session_key is not None:
      env['BW_SESSION'] = self.state.session_key
    if self.state.data_dir is not None:
      env['BITWARDENCLI_APPDATA_DIR'] = str(self.state.data_dir)
    return env


  @overload
  def run_command(
    self,
    command: Sequence[str],
    *,
    background: Literal[True],
  ) -> Popen[bytes]: ...
  
  @overload
  def run_command(
    self,
    command: Sequence[str],
    *,
    background: Literal[False] = False,
    input: bytes|None = None,
  ) -> CompletedProcess[bytes]: ...


  def run_command(
    self,
    command: Sequence[str],
    *,
    background: bool = False,
    input: bytes|None = None,
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
      log.error(msg)
      raise

    return r
