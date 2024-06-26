from __future__ import annotations
from typing import Any, cast
from pathlib import Path
import logging

from .services import AuthService, ImportExportService, MiscService, ApiService, ConfigService
from .connection import CliConnection
from pywarden.login_credentials import EmailCredentials
from pywarden.constants import StatusResponse, AuthStatusResponse, DEFAULT_SERVER
from .state import CliState


log = logging.getLogger(__name__)


class CliControl:
  state: CliState
  _auth_service: AuthService
  _import_export_service: ImportExportService
  _api_service: ApiService
  _misc_service: MiscService
  _config_service: ConfigService

  def __init__(self,
    state: CliState,
    auth_service: AuthService,
    import_export_service: ImportExportService,
    api_service: ApiService,
    misc_service: MiscService,
    config_service: ConfigService,
    server: str = DEFAULT_SERVER,
  ) -> None:
    self.state = state
    self._auth_service = auth_service
    self._import_export_service = import_export_service
    self._api_service = api_service
    self._misc_service = misc_service
    self._config_service = config_service

    # method shortcuts
    self.get_export = self._import_export_service.get_export
    self.serve_api = self._api_service.serve
    self.status = self._misc_service.status
    self.get_server = self._config_service.get_server

    # apply config stuff
    self.set_server(server)

    log.info(self.formatted_status())


  def is_logged_in(self, status: StatusResponse|None = None):
    status = status or self.status()
    return status['status'] != 'unauthenticated'

  def is_locked(self, status: StatusResponse|None = None):
    status = status or self.status()
    return status['status'] != 'unlocked'


  def login(self, creds: EmailCredentials, status: StatusResponse|None = None):
    status = status or self.status()
    if self.is_logged_in(status):
      log.info(f"Already authenticated, logging out and back in")
      self.logout()
    self._auth_service.login(creds)

  def logout(self):
    self._auth_service.logout()

  def lock(self):
    self._auth_service.lock()
    self.state.session_key = None

  def unlock(self, password: str):
    key = self._auth_service.unlock(password)
    self.state.session_key = key


  def set_server(self, url: str, status: StatusResponse|None = None):
    status = status or self.status()
    # can only change server if not logged in
    if url != status['serverUrl'] and self.is_logged_in(status):
      log.info(f"Cannot change server to {url} when logged in, logging out")
      self.logout()
    self._config_service.set_server(url)


  # cli connection shortcuts

  @property
  def session_key(self) -> str|None:
    return self.state.session_key
  @session_key.setter
  def session_key(self, value: str) -> None:
    self.state.session_key = value
  @property
  def cli_path(self) -> Path:
    return self.state.cli_path
  @property
  def data_dir(self) -> Path|None:
    return self.state.data_dir
  

  def formatted_status(self, status: StatusResponse|None = None) -> str:
    status = status or self.status()

    r = 'Current Status: '
    if self.is_logged_in(status):
      status = cast(AuthStatusResponse, status)
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
  def create(cli_path: Path, server: str = DEFAULT_SERVER, session_key: str|None = None, data_dir: Path|None = None) -> CliControl:
    state = CliState(
      cli_path = cli_path.resolve(),
      session_key = session_key,
      data_dir = data_dir
    )
    conn = CliConnection(state)
    return CliControl(
      state=state,
      auth_service=AuthService(conn),
      import_export_service=ImportExportService(conn),
      api_service=ApiService(conn),
      misc_service=MiscService(conn),
      config_service=ConfigService(conn),
      server=server
    )
