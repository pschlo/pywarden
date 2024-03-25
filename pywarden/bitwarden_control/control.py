from __future__ import annotations
from dataclasses import dataclass
from subprocess import Popen, CalledProcessError
import subprocess
import json
from pathlib import Path
from typing import Any, ContextManager, TypedDict, Literal, cast
from collections.abc import Sequence
import time
import requests
import math

from pywarden.cli import CliControl, StatusResponse, AuthStatusResponse, CliState, CliConnection, EmailCredentials
from pywarden.api import ApiConnection, ApiState
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
  def create_from_cli(
    cli: CliControl,
    api_config: ApiConfig,
    master_password: str,
    credentials: EmailCredentials|None = None,
    logout_on_shutdown: bool = True
  ) -> BitwardenControl:
    
    # prepare for API
    status = cli.get_status()

    if credentials is not None:
      cli.login(credentials, status)
    else:
      if not cli.is_logged_in(status):
        raise RuntimeError(f"Not logged in and no login credentials provided")
      print("No credentials provided, using authenticated account")

    print("Unlocking vault")
    cli.unlock(master_password)
    
    print("Starting API")
    process = cli.serve_api(port=api_config.port, host=api_config.hostname)

    # create API object
    api = LocalApiControl.create(process, port=api_config.port, host=api_config.hostname)

    return BitwardenControl(api, cli, timeout_secs=api_config.startup_timeout_secs, logout_on_shutdown=logout_on_shutdown)


  @staticmethod
  def create(
    cli_config: CliConfig,
    api_config: ApiConfig,
    master_password: str,
    credentials: EmailCredentials|None = None,
    logout_on_shutdown: bool = True
  ) -> BitwardenControl:

    print("Creating CLI control")
    cli = CliControl.create(cli_path=cli_config.cli_path, data_dir=cli_config.data_dir)
    status = cli.get_status()

    # set config
    if cli_config.server is not None:
      cli.set_server(cli_config.server, status=status)
      status = cli.get_status()

    return BitwardenControl.create_from_cli(
      cli=cli,
      api_config=api_config,
      master_password=master_password,
      credentials=credentials,
      logout_on_shutdown=logout_on_shutdown
    )
    


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
    except (TimeoutError, CalledProcessError) as e:
      print(f"{e.__class__.__name__}: {e}")

    if logout:
      print(f"  Logging out")
      try:
        self.cli.logout()
      except (TimeoutError, CalledProcessError) as e:
        print(f"{e.__class__.__name__}: {e}")
