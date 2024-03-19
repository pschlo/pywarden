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

from pywarden.cli import CliControl, StatusResponse, AuthenticatedStatusResponse, CliConnection, CliConfig
from pywarden.api import LoginCredentials, ApiConnection
from ..local_api.control import LocalApiControl
from ..local_api.config import ApiConfig



"""
Upon creation, ensures that:
  - user is logged in
  - vault is unlocked
The session token is then used to serve the API.
"""
class BitwardenControl(ContextManager):
  api: LocalApiControl
  cli: CliControl


  def __init__(self, api: LocalApiControl, cli: CliControl) -> None:
    self.api = api
    self.cli = cli

    self.wait_until_ready()


  @staticmethod
  def create(api_config: ApiConfig, cli_config: CliConfig, master_password: str, credentials: LoginCredentials|None = None) -> BitwardenControl:
    # create CLI object
    conn = CliConnection(cli_config.path)
    cli = CliControl.create(conn)
    
    # prepare for API
    BitwardenControl.login(cli, credentials)
    BitwardenControl.unlock(cli, master_password)
    
    # start the API
    process = cli.serve_api(port=api_config.port, host=api_config.hostname)

    # create API object
    conn = ApiConnection('http', port=api_config.port, host=api_config.hostname)
    api = LocalApiControl.create(conn, process)

    return BitwardenControl(api, cli)


  # TODO: Move to CliControl
  @staticmethod
  def login(cli: CliControl, credentials: LoginCredentials|None) -> None:
    print("Checking status")
    status = cli.get_status()

    if status['status'] == 'unauthenticated':
      print("Status: Not logged in")
      if credentials is not None:
        print(f"Logging in as {credentials['email']}")
        cli.login(credentials['email'], credentials['password'])
      else:
        raise RuntimeError(f"Not logged in and no credentials provided")

    else:
      status = cast(AuthenticatedStatusResponse, status)
      print(f"Status: Logged in as {status['userEmail']}")
      # if credentials were given, the email should match. Otherwise, log out and back in
      if credentials is not None:
        if status['userEmail'] != credentials['email']:
          print(f"Should be using account '{credentials['email']}', logging out and back in")
          cli.logout()
          BitwardenControl.login(cli, credentials)


  @staticmethod
  def unlock(cli: CliControl, password: str) -> None:
    print("Unlocking vault")
    cli.unlock(password)

  def __enter__(self) -> BitwardenControl:
    return self
  
  def __exit__(self, typ, val, tb) -> None:
    self.shutdown()

  def wait_until_ready(self, timeout_secs: float = 10):
    try:
      self.api.wait_until_ready(timeout_secs)
    except TimeoutError:
      self.shutdown()
      raise

  def shutdown(self) -> None:
    print(f"Shutting down Bitwarden Control")
    print(f"  Stopping API")
    self.api.shutdown()
    print(f"  Locking vault")
    self.cli.lock()
    print(f"  Logging out")
    self.cli.logout()
