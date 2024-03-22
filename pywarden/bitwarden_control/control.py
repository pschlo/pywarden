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

from pywarden.cli import CliControl, StatusResponse, AuthenticatedStatusResponse, CliConnection, EmailCredentials
from pywarden.api import ApiConnection
from pywarden.local_api import LocalApiControl
from .local_api_config import ApiConfig
from .cli_config import CliConfig


class BitwardenControl(ContextManager):
  api: LocalApiControl
  cli: CliControl
  logout_on_shutdown: bool


  def __init__(self, api: LocalApiControl, cli: CliControl, *, timeout_secs: float|None = None, logout_on_shutdown: bool) -> None:
    self.api = api
    self.cli = cli
    self.logout_on_shutdown = logout_on_shutdown

    self.wait_until_ready(timeout_secs)


  @staticmethod
  def create(
    api_config: ApiConfig,
    cli_config: CliConfig,
    master_password: str,
    credentials: EmailCredentials|None = None,
    logout_on_shutdown: bool = True
  ) -> BitwardenControl:
    print("Creating CLI control")
    conn = CliConnection(cli_config.path)
    cli = CliControl.create(conn)
    
    # prepare for API

    if credentials is not None:
      cli.login(credentials)
    else:
      if not cli.is_logged_in:
        raise RuntimeError(f"Not logged in and no login credentials provided")
      print("No credentials provided, using authenticated account")

    print("Unlocking vault")
    cli.unlock(master_password)
    
    print("Starting API")
    process = cli.serve_api(port=api_config.port, host=api_config.hostname)

    # create API object
    conn = ApiConnection('http', port=api_config.port, host=api_config.hostname)
    api = LocalApiControl.create(conn, process)

    return BitwardenControl(api, cli, timeout_secs=api_config.startup_timeout_secs, logout_on_shutdown=logout_on_shutdown)

  def __enter__(self) -> BitwardenControl:
    return self
  
  def __exit__(self, typ, val, tb) -> None:
    self.shutdown()

  def wait_until_ready(self, timeout_secs: float|None = None):
    try:
      self.api.wait_until_ready(timeout_secs)
    except TimeoutError:
      self.shutdown()
      raise

  def shutdown(self, logout: bool|None = None) -> None:
    if logout is None:
      logout = self.logout_on_shutdown

    print(f"Shutting down Bitwarden Control")

    print(f"  Stopping API")
    try:
      self.api.shutdown()
    except TimeoutError as e:
      print(f"TimeoutError: {e}")

    print(f"  Locking vault")
    try:
      self.cli.lock()
    except TimeoutError as e:
      print(f"TimeoutError: {e}")

    if logout:
      print(f"  Logging out")
      try:
        self.cli.logout()
      except TimeoutError as e:
        print(f"TimeoutError: {e}")
