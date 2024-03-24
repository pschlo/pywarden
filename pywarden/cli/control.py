from __future__ import annotations
from typing import Any, cast
from pathlib import Path

from .services import AuthService, ImportExportService, MiscService, ApiService, ConfigService
from .connection import CliConnection
from .login_credentials import EmailCredentials
from .cli_responses import StatusResponse, AuthenticatedStatusResponse, DEFAULT_SERVER


class CliControl:
  conn: CliConnection
  _auth_service: AuthService
  _import_export_service: ImportExportService
  _api_service: ApiService
  _misc_service: MiscService
  _config_service: ConfigService

  def __init__(self,
    conn: CliConnection,
    auth_service: AuthService,
    import_export_service: ImportExportService,
    api_service: ApiService,
    misc_service: MiscService,
    config_service: ConfigService
  ) -> None:
    self.conn = conn
    self._auth_service = auth_service
    self._import_export_service = import_export_service
    self._api_service = api_service
    self._misc_service = misc_service
    self._config_service = config_service

    # method shortcuts
    self.get_export = self._import_export_service.get_export
    self.serve_api = self._api_service.serve
    self.get_status = self._misc_service.get_status
    self.get_server = self._config_service.get_server


  def is_logged_in(self, status: StatusResponse|None = None):
    if status is None:
      status = self.get_status()
    return status['status'] != 'unauthenticated'

  def is_locked(self, status: StatusResponse|None = None):
    if status is None:
      status = self.get_status()
    return status['status'] != 'unlocked'


  def login(self, creds: EmailCredentials, status: StatusResponse|None = None):
    if status is None:
      status = self.get_status()

    if self.is_logged_in(status):
      print(f"Already authenticated, logging out and back in")
      self.logout()
      self.login(creds)
      return

    print(f"Logging in as {creds['email']} on {self.get_server()}")
    self._auth_service.login(creds)

  def logout(self):
    self._auth_service.logout()

  def lock(self):
    self._auth_service.lock()
    self.conn.session_key = None

  def unlock(self, password: str):
    key = self._auth_service.unlock(password)
    self.conn.session_key = key


  def set_server(self, url: str, status: StatusResponse|None = None):
    if status is None:
      status = self.get_status()

    # can only change server if not logged in
    if url != self.get_status()['serverUrl'] and self.is_logged_in(status):
      print(f"Cannot change server to {url} when logged in, logging out")
      self.logout()
    self._config_service.set_server(url)


  # cli connection shortcuts

  @property
  def session_key(self) -> str|None:
    return self.conn.session_key
  @session_key.setter
  def session_key(self, value: str) -> None:
    self.conn.session_key = value

  @property
  def cli_path(self) -> Path:
    return self.conn.cli_path
  @cli_path.setter
  def cli_path(self, value: Path) -> None:
    self.conn.cli_path = value

  @property
  def data_dir(self) -> Path|None:
    return self.conn.data_dir
  @data_dir.setter
  def data_dir(self, value: Path) -> None:
    self.conn.data_dir = value
  

  def get_formatted_status(self, status: StatusResponse|None = None) -> str:
    if status is None:
      status = self.get_status()

    r = 'Current Status: '
    if self.is_logged_in(status):
      status = cast(AuthenticatedStatusResponse, status)
      r += f"Logged in as {status['userEmail']} at {status['serverUrl']}"
    else:
      r += f"Not logged in"
    r += ", "
    if self.is_locked(status):
      r += "vault locked"
    else:
      r += "vault unlocked"
    return r

  @staticmethod
  def create(conn: CliConnection) -> CliControl:
    return CliControl(
      conn=conn,
      auth_service=AuthService(conn),
      import_export_service=ImportExportService(conn),
      api_service=ApiService(conn),
      misc_service=MiscService(conn),
      config_service=ConfigService(conn)
    )
