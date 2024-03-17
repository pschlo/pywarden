from __future__ import annotations
from dataclasses import dataclass
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
from .active_local_api_server import ActiveLocalApiServer
from .cli_responses import StatusResponse, AuthenticatedStatusResponse
from .local_api_config import LocalApiConfig
from .login_credentials import LoginCredentials


TIMEOUT_SECS = 10




"""
Upon creation, ensures that:
  - user is logged in
  - vault is unlocked
The session token is then used to serve the API.
"""
class LocalApiServer(ContextManager):
  config: LocalApiConfig
  cli: BitwardenCli
  active_server: ActiveLocalApiServer | None = None


  def __init__(self, config: LocalApiConfig, cli: BitwardenCli, master_password: str, credentials: LoginCredentials|None = None) -> None:
    self.config = config
    self.cli = cli
    self.login(credentials)
    self.unlock(master_password)

  def login(self, credentials: LoginCredentials|None) -> None:
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
          self.login(credentials)

  def unlock(self, password: str) -> None:
    print("Unlocking vault")
    self.cli.unlock(password)

  def __enter__(self) -> ActiveLocalApiServer:
    self.active_server = self.create()
    return self.active_server
  
  def __exit__(self, typ, val, tb) -> None:
    assert self.active_server is not None
    self.active_server.shutdown()


  def create(self) -> ActiveLocalApiServer:
    print("Preparing API Server")

    command = ['serve', '--port', str(self.config.port), '--hostname', self.config.hostname]
    process = self.cli.run_background_command(command)
    active_server = ActiveLocalApiServer(process, config=self.config, cli=self.cli)
    LocalApiServer.wait_until_ready(active_server)

    print(f"Now serving Vault Management API on port {self.config.port}")
    return active_server
  

  @staticmethod
  def wait_until_ready(server: ActiveLocalApiServer):
    success = False
    t0 = time.perf_counter()
    
    while time.perf_counter() - t0 < TIMEOUT_SECS:
      try:
        server.get('/status')
        success = True
        break
      except requests.ConnectionError:
        pass
      except requests.RequestException:
        break
      time.sleep(0.1)

    if not success:
      server.shutdown()
      raise TimeoutError(f"API server failed to start after {TIMEOUT_SECS} seconds")
