from __future__ import annotations
from dataclasses import dataclass
from subprocess import Popen, CalledProcessError
import subprocess
import json
from pathlib import Path
from typing import Any, ContextManager, TypedDict, Literal, cast, Iterator, Iterable
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
import requests
from .auth_control import LoggedInControl, UnlockedControl


"""
api property is set iff api server running iff logged in
"""
class BitwardenControl:
  cli: CliControl
  api_conf: ApiConfig

  def __init__(self, cli: CliControl, api_conf: ApiConfig) -> None:
    self.cli = cli
    self.api_conf = api_conf

    self.get_export = self.cli.get_export


  @staticmethod
  def create(
    cli_conf: CliConfig,
    api_conf: ApiConfig,
  ) -> BitwardenControl:
    print("Creating CLI control")
    cli = CliControl.create(cli_path=cli_conf.cli_path, data_dir=cli_conf.data_dir, server=cli_conf.server)
    return BitwardenControl(cli, api_conf)
  

  @contextmanager
  def login(self, creds: EmailCredentials) -> Iterator[LoggedInControl]:
    status = self.status()
    print(f"Logging in as {creds['email']} at {self.cli.get_server()}")
    try:
      self.cli.login(creds, status)
      c = LoggedInControl.create(self.cli, self.api_conf)
      yield c
    finally:
      c.stop_api()
      c.logout()

  @contextmanager
  def as_logged_in(self) -> Iterator[LoggedInControl]:
    try:
      c = LoggedInControl.create(self.cli, self.api_conf)
      yield c
    finally:
      c.stop_api()
  
  @contextmanager
  def login_unlock(self, creds: EmailCredentials, password: str) -> Iterator[UnlockedControl]:
    with self.login(creds) as a:
      with a.unlock(password) as b:
        yield b

  @contextmanager
  def login_unlock_interactive(self, email: str|None = None) -> Iterator[UnlockedControl]:
    status = self.status()

    if email is None:
      r = None
      while (r is None) or not len(r) > 0:
        r = input("Email: ").strip()
      email = r

    if self.is_logged_in(status) and cast(AuthStatusResponse, status)['userEmail'] == email and status['serverUrl'] == self.cli.get_server():
      # already logged in
      login_context = self.as_logged_in()
      password = ask_master_password()
    else:
      # not logged in or logged in as wrong user
      creds = ask_email_credentials(email)
      login_context = self.login(creds)
      password = creds['password']

    with login_context as a:
      with a.unlock(password) as b:
        yield b


  def status(self) -> StatusResponse:
    return self.cli.status()
    
  def is_logged_in(self, status: StatusResponse|None = None) -> bool:
    status = status or self.status()
    return status['status'] != 'unauthenticated'

  def is_locked(self, status: StatusResponse|None = None) -> bool:
    status = status or self.status()
    return status['status'] != 'unlocked'
