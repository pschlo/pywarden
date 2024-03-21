from __future__ import annotations
import os

from .services import AuthService, ImportExportService, MiscService, ApiService
from .connection import CliConnection
from .login_credentials import LoginCredentials
from .cli_responses import StatusResponse


class CliControl:
  _auth: AuthService
  _import_export: ImportExportService
  _api: ApiService
  _misc: MiscService

  is_logged_in: bool
  _session_key: str|None = None

  @property
  def is_locked(self):
    return self._session_key is None
  
  @property
  def session_key(self) -> str|None:
    return self._session_key
  
  @session_key.setter
  def session_key(self, value: str|None) -> None:
    self._session_key = value
    if value is None:
      os.environ.pop('BW_SESSION', None)
    else:
      os.environ['BW_SESSION'] = value


  def __init__(self,
    auth: AuthService,
    import_export: ImportExportService,
    api: ApiService,
    misc: MiscService
  ) -> None:
    self._auth = auth
    self._import_export = import_export
    self._api = api
    self._misc = misc

    # method shortcuts
    self.get_export = self._import_export.get_export
    self.serve_api = self._api.serve
    self.get_status = self._misc.get_status

    status = self.get_status()['status']
    assert status != 'unlocked'  # cannot possibly be unlocked without session key
    self.is_logged_in = False if status == 'unauthenticated' else True


  def login(self, credentials: LoginCredentials, status: StatusResponse):
    self._auth.login(credentials, status)
    self.is_logged_in = True

  def logout(self):
    self._auth.logout()
    self.is_logged_in = False

  def lock(self):
    self._auth.lock()
    self.session_key = None

  def unlock(self, password: str):
    key = self._auth.unlock(password)
    self.session_key = key

  @staticmethod
  def create(conn: CliConnection) -> CliControl:
    return CliControl(
      auth=AuthService(conn),
      import_export=ImportExportService(conn),
      api=ApiService(conn),
      misc=MiscService(conn)
    )
