from __future__ import annotations
from typing import Any, cast, overload
from collections.abc import Iterator
from contextlib import contextmanager
import logging
import shutil
from pathlib import Path

from pywarden.cli import CliControl, StatusResponse, AuthStatusResponse, EmailCredentials
from pywarden.utils import ask_email_credentials, ask_master_password
from .config import CliConfig, ApiConfig
from .logged_in_control import LoggedInBwControl
from .unlocked_control import UnlockedBwControl


log = logging.getLogger(__name__)


"""
api property is set iff api server running iff logged in
"""
class BaseBwControl:
  cli: CliControl
  api_conf: ApiConfig


  @overload
  def __init__(self, cli: CliConfig|None = None, api: ApiConfig|None = None): ...
  @overload
  def __init__(self, cli: CliControl, api: ApiConfig|None = None): ...
  def __init__(self, cli: CliControl|CliConfig|None = None, api: ApiConfig|None = None) -> None:
    cli = cli or CliConfig()
    api = api or ApiConfig()

    if isinstance(cli, CliConfig):
      conf = cli
      log.info("Creating CLI control")
      if conf.cli_path is None:
        # search in PATH
        r = shutil.which('bw')
        if r is None:
          raise ValueError(f'Could not locate Bitwarden CLI executable')
        conf.cli_path = Path(r)
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
  def login(self, creds: EmailCredentials) -> Iterator[LoggedInBwControl]:
    status = self.status()
    log.info(f"Logging in as {creds['email']} at {self.cli.get_server()}")

    try:
      self.cli.login(creds, status)
      c = LoggedInBwControl(self.cli, self.api_conf)
    except:
      try: self.cli.logout()
      except Exception as e: log.error(f"{e.__class__.__name__}: {e}")
      raise

    try:
      yield c
    finally:
      c.stop_api()
      c.logout()

  @contextmanager
  def as_logged_in(self) -> Iterator[LoggedInBwControl]:
    c = LoggedInBwControl(self.cli, self.api_conf)
    try:
      yield c
    finally:
      c.stop_api()
  
  @contextmanager
  def login_unlock(self, creds: EmailCredentials, password: str) -> Iterator[UnlockedBwControl]:
    with self.login(creds) as a:
      with a.unlock(password) as b:
        yield b

  @contextmanager
  def login_unlock_interactive(self, email: str|None = None) -> Iterator[UnlockedBwControl]:
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
  def with_session_key(self, key: str) -> Iterator[UnlockedBwControl]:
    self.cli.session_key = key
    with self.as_logged_in() as c:
      with c.as_unlocked() as u:
        yield u
