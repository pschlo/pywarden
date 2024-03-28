from __future__ import annotations
from typing import Any, cast, overload
from collections.abc import Iterator
from contextlib import contextmanager

from pywarden.cli import CliControl, StatusResponse, AuthStatusResponse, EmailCredentials
from pywarden.utils import ask_email_credentials, ask_master_password
from .config import CliConfig, ApiConfig
from .logged_in_control import LoggedInControl
from .unlocked_control import UnlockedControl


"""
api property is set iff api server running iff logged in
"""
class BitwardenControl:
  cli: CliControl
  api_conf: ApiConfig


  @overload
  def __init__(self, cli: CliConfig, api: ApiConfig): ...
  @overload
  def __init__(self, cli: CliControl, api: ApiConfig): ...
  def __init__(self, cli: CliControl|CliConfig, api: ApiConfig) -> None:
    if isinstance(cli, CliConfig):
      conf = cli
      print("Creating CLI control")
      cli = CliControl.create(cli_path=conf.cli_path, data_dir=conf.data_dir, server=conf.server)

    self.cli = cli
    self.api_conf = api
    self.status = self.cli.status


  @property
  def data_dir(self):
    return self.cli.data_dir
  @property
  def cli_path(self):
    return self.cli.cli_path
  

  @contextmanager
  def login(self, creds: EmailCredentials) -> Iterator[LoggedInControl]:
    status = self.status()
    print(f"Logging in as {creds['email']} at {self.cli.get_server()}")

    try:
      self.cli.login(creds, status)
      c = LoggedInControl(self.cli, self.api_conf)
    except:
      try: self.cli.logout()
      except Exception as e: print(f"{e.__class__.__name__}: {e}")
      raise

    try:
      yield c
    finally:
      c.stop_api()
      c.logout()

  @contextmanager
  def as_logged_in(self) -> Iterator[LoggedInControl]:
    c = LoggedInControl(self.cli, self.api_conf)
    try:
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
    
  def is_logged_in(self, status: StatusResponse|None = None) -> bool:
    status = status or self.status()
    return status['status'] != 'unauthenticated'

  def is_locked(self, status: StatusResponse|None = None) -> bool:
    status = status or self.status()
    return status['status'] != 'unlocked'
  
  @contextmanager
  def with_session_key(self, key: str) -> Iterator[UnlockedControl]:
    self.cli.session_key = key
    with self.as_logged_in() as c:
      with c.as_unlocked() as u:
        yield u
