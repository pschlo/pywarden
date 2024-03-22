from __future__ import annotations
from subprocess import Popen, PIPE, CompletedProcess
from pathlib import Path
from typing import Any, overload, Literal
from collections.abc import Sequence


"""
Low-level communication interface to local Bitwarden CLI
"""
class CliConnection:
  path: Path

  def __init__(self, path: Path) -> None:
    self.path = path


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
    
    proc = Popen([str(self.path), *command], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    if background:
      return proc
    stdout, stderr = proc.communicate(input)
    return CompletedProcess(proc.args, proc.returncode, stdout=stdout, stderr=stderr)
