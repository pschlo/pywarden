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
from .controller import Controller
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
  cli: Cli
  active_control: Controller | None = None


  def __init__(self, config: ApiConfig, cli: Cli, master_password: str, credentials: LoginCredentials|None = None) -> None:
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

  def __enter__(self) -> Controller:
    self.active_control = self.create()
    return self.active_control
  
  def __exit__(self, typ, val, tb) -> None:
    assert self.active_control is not None
    self.active_control.shutdown()


  def create(self) -> Controller:
    print("Preparing API Server")

    # start the API
    process = self.cli.serve_api(port=self.config.port, host=self.config.hostname)

    # create API object
    conn = ApiConnection('http', port=self.config.port, host=self.config.hostname)
    api = LocalApi.create(conn, process)

    # create controller
    controller = Controller(api, self.cli)
    BitwardenControl.wait_until_ready(controller)

    print(f"Now serving Vault Management API on port {self.config.port}")
    return controller
  

  @staticmethod
  def wait_until_ready(controller: Controller):
    success = False
    t0 = time.perf_counter()
    
    while time.perf_counter() - t0 < TIMEOUT_SECS:
      try:
        controller.api.status()
        success = True
        break
      except requests.ConnectionError:
        pass
      except requests.RequestException:
        break
      time.sleep(0.1)

    if not success:
      controller.shutdown()
      raise TimeoutError(f"API server failed to start after {TIMEOUT_SECS} seconds")
