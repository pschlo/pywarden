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
from contextlib import contextmanager

from pywarden.cli import CliControl, StatusResponse, AuthStatusResponse, CliState, CliConnection, EmailCredentials
from pywarden.api import ApiConnection, ApiState
from pywarden.utils import ask_email_credentials, ask_master_password
from pywarden.local_api import LocalApiControl
from .local_api_config import ApiConfig
from .cli_config import CliConfig


"""
api property is set iff api server running iff logged in
"""
class BitwardenControl:
  _api: LocalApiControl|None = None
  cli: CliControl
  api_conf: ApiConfig

  @property
  def api(self) -> LocalApiControl:
    if self._api is None:
      raise RuntimeError(f"Cannot access API when logged out")
    return self._api


  def __init__(self, cli: CliControl, api_conf: ApiConfig) -> None:
    self.cli = cli
    self.api_conf = api_conf

    if cli.is_logged_in():
      self._start_api()

    self.get_export = self.cli.get_export


  @staticmethod
  def create(
    cli_config: CliConfig,
    api_conf: ApiConfig,
  ) -> BitwardenControl:
    print("Creating CLI control")
    cli = CliControl.create(cli_path=cli_config.cli_path, data_dir=cli_config.data_dir, server=cli_config.server)
    return BitwardenControl(cli, api_conf)
  
  def _start_api(self) -> None:
    print(f"Starting API server")
    process = self.cli.serve_api(host=self.api_conf.hostname, port=self.api_conf.port)
    self._api = LocalApiControl.create(process, host=self.api_conf.hostname, port=self.api_conf.port)
    self.api.wait_until_ready()

  def _stop_api(self) -> None:
    print(f"Stopping API server")
    self.api.shutdown()
    self._api = None


  def login(self, creds: EmailCredentials) -> ContextManager:
    status = self.status()
    print(f"Logging in as {creds['email']} at {self.cli.get_server()}")
    self.cli.login(creds, status)
    self._start_api()
    return self._login_session()

  @contextmanager
  def _login_session(self):
    try:
      yield
    finally:
      self.logout()
  
    
  def logout(self) -> None:
    print("Logging out")
    self._stop_api()
    self.cli.logout()

  # unlock API and CLI
  def unlock(self, password: str) -> ContextManager:
    print(f"Unlocking vault")
    key = self.api.unlock(password)
    self.cli.session_key = key
    return self._unlock_session()

  @contextmanager
  def _unlock_session(self):
    try:
      yield
    finally:
      self.lock()

  def lock(self) -> None:
    print(f"Locking vault")
    self.cli.lock()
    if self._api is not None:
      self._api.lock()

  def status(self) -> StatusResponse:
    if self._api is not None:
      return self._api.status()
    else:
      return self.cli.status()
    
  def is_logged_in(self, status: StatusResponse|None = None) -> bool:
    if status is None:
      status = self.status()
    return status['status'] != 'unauthenticated'

  def is_locked(self, status: StatusResponse|None = None) -> bool:
    if status is None:
      status = self.status()
    return status['status'] != 'unlocked'


  def login_unlock_interactive(self, email: str|None = None) -> ContextManager:
    status = self.status()

    if email is None:
      r = None
      while (r is None) or not len(r) > 0:
        r = input("Email: ").strip()
      email = r

    if self.is_logged_in(status) and cast(AuthStatusResponse, status)['userEmail'] == email and status['serverUrl'] == self.cli.get_server():
      # already logged in
      self.unlock(ask_master_password(email))
      return self._login_unlock_session(logout=False)
    else:
      # not logged in or logged in as wrong user
      creds = ask_email_credentials(email)
      self.login(creds)
      self.unlock(creds['password'])
      return self._login_unlock_session(logout=True)    

  @contextmanager
  def _login_unlock_session(self, logout: bool):
    try:
      yield
    finally:
      self.lock()
      if logout:
        self.logout()


  def get_items(self):
    return self.api.get_items()
