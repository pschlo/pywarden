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

from .bitwarden_cli import BitwardenCli
from .active_api_server import ActiveApiServer
from .cli_responses import StatusResponse, AuthenticatedStatusResponse



class Credentials(TypedDict):
  email: str
  password: str



# performs login if credentials are provided
class ApiServer(ContextManager):
  cli: BitwardenCli
  active_server: ActiveApiServer | None = None


  def __init__(self, cli: BitwardenCli, credentials: Credentials|None = None) -> None:
    self.cli = cli
    self.ensure_login(credentials)


  def ensure_login(self, credentials: Credentials|None) -> None:
    print("Checking status")
    status = self.cli.get_status()

    if status['status'] == 'unauthenticated':
      print("Status: Not logged in")
      if credentials is not None:
        print(f"Logging in as {credentials['email']}")
        self.cli.login(credentials['email'], credentials['password'])
      else:
        raise RuntimeError(f"Not logged in and no credentials provided")

    else:
      status = cast(AuthenticatedStatusResponse, status)
      print(f"Status: Logged in as {status['userEmail']}")
      # if credentials were given, the email should match. Otherwise, log out and back in
      if credentials is not None:
        if status['userEmail'] != credentials['email']:
          print(f"Should be using account '{credentials['email']}', logging out and back in")
          self.cli.logout()
          self.ensure_login(credentials)

  def __enter__(self) -> ActiveApiServer:
    self.active_server = self.create()
    return self.active_server
  
  def __exit__(self, typ, val, tb) -> None:
    assert self.active_server is not None
    self.active_server.stop()

  

  def create(self, port: int = 8087, hostname: str|None = None) -> ActiveApiServer:
    print("Preparing API Server")

    command = [str(self.cli.path), 'serve', '--port', str(port)]
    if hostname is not None:
      command += ['--hostname', hostname]

    active_server = ActiveApiServer(Popen(command), port, hostname)
    active_server.wait_until_ready()

    print(f"Now serving Vault Management API on port {port}")

    return active_server
