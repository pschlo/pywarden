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

from pywarden.cli import CliControl, StatusResponse, AuthenticatedStatusResponse, CliConnection, LoginCredentials
from pywarden.api import ApiConnection
from pywarden.local_api import LocalApiControl
from .local_api_config import ApiConfig
from .cli_config import CliConfig



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
  def create(api_config: ApiConfig, cli_config: CliConfig, master_password: str, credentials: LoginCredentials) -> BitwardenControl:
    # create CLI object
    conn = CliConnection(cli_config.path)
    cli = CliControl.create(conn)

    print("Getting status")
    status = cli.get_status()
    
    # prepare for API
    print("Logging in")
    cli.login(credentials, status)
    print("Unlocking vault")
    cli.unlock(master_password)
    
    # start the API
    process = cli.serve_api(port=api_config.port, host=api_config.hostname)

    # create API object
    conn = ApiConnection('http', port=api_config.port, host=api_config.hostname)
    api = LocalApiControl.create(conn, process)

    return BitwardenControl(api, cli)

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
