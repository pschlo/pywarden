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

from pywarden.cli import Cli, StatusResponse, AuthenticatedStatusResponse
from pywarden.api import LoginCredentials, ApiConnection
from .local_api import LocalApi
from .api_config import ApiConfig


TIMEOUT_SECS = 10




"""
Upon creation, ensures that:
  - user is logged in
  - vault is unlocked
The session token is then used to serve the API.
"""
class BitwardenControl(ContextManager):
  config: ApiConfig
  api: LocalApi
  cli: Cli


  def __init__(self, config: ApiConfig, cli: Cli, master_password: str, credentials: LoginCredentials|None = None) -> None:
    self.config = config
    self.cli = cli
    self.login(credentials)
    self.unlock(master_password)

     # start the API
    process = self.cli.serve_api(port=self.config.port, host=self.config.hostname)

    # create API object
    conn = ApiConnection('http', port=self.config.port, host=self.config.hostname)
    self.api = LocalApi.create(conn, process)

    self.api.wait_until_ready()

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

  def __enter__(self) -> BitwardenControl:
    return self
  
  def __exit__(self, typ, val, tb) -> None:
    self.shutdown()

  def wait_until_ready(self):
    try:
      self.api.wait_until_ready()
    except TimeoutError:
      self.shutdown()

  def shutdown(self) -> None:
    print(f"Shutting down Bitwarden Control")
    print(f"  Stopping API")
    self.api.shutdown()
    print(f"  Locking vault")
    self.cli.lock()
    print(f"  Logging out")
    self.cli.logout()
