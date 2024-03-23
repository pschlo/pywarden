from __future__ import annotations
from typing import Any, cast

from .services import AuthService, ImportExportService, MiscService, ApiService, ConfigService
from .connection import CliConnection
from .login_credentials import EmailCredentials
from .cli_responses import StatusResponse, AuthenticatedStatusResponse


class CliControl:
  conn: CliConnection
  _auth_service: AuthService
  _import_export_service: ImportExportService
  _api_service: ApiService
  _misc_service: MiscService
  _config_service: ConfigService

  status: StatusResponse  # cached status response

  @property
  def is_logged_in(self):
    return self.status['status'] != 'unauthenticated'

  @property
  def is_locked(self):
    return self.status['status'] != 'unlocked'

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
    self.set_server = self._config_service.set_server

    # get initial status
    self.status = self.get_status()
    assert self.is_locked  # cannot possibly be unlocked without session key
    print(self.get_formatted_status())

  def login(self, credentials: EmailCredentials):
    self._auth_service.login(credentials, self.status)
    self.status = self.get_status()
    assert self.is_logged_in

  def logout(self):
    self._auth_service.logout()
    self.status = self.get_status()
    assert not self.is_logged_in

  def lock(self):
    self._auth_service.lock()
    self.conn.session_key = None
    self.status = self.get_status()
    assert self.is_locked

  def unlock(self, password: str):
    key = self._auth_service.unlock(password)
    self.conn.session_key = key
    self.status = self.get_status()
    assert not self.is_locked

  def get_formatted_status(self) -> str:
    r = 'Current Status: '
    if self.is_logged_in:
      status = cast(AuthenticatedStatusResponse, self.status)
      r += f"Logged in as {status['userEmail']} on {status['serverUrl']}"
    else:
      r += f"Not logged in"
    r += ", "
    if self.is_locked:
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
