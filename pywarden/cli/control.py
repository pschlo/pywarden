from __future__ import annotations
import os

from .services import AuthService, ImportExportService, MiscService, ApiService
from .connection import CliConnection
from .login_credentials import EmailCredentials
from .cli_responses import StatusResponse


class CliControl:
  _auth: AuthService
  _import_export: ImportExportService
  _api: ApiService
  _misc: MiscService

  status: StatusResponse  # cached status response

  @property
  def is_logged_in(self):
    return self.status['status'] != 'unauthenticated'

  @property
  def is_locked(self):
    return self.status['status'] != 'unlocked'
  
  @property
  def session_key(self) -> str|None:
    return os.environ.get('BW_SESSION', None)
  
  @session_key.setter
  def session_key(self, value: str|None) -> None:
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

    self.status = self.get_status()
    assert self.is_locked  # cannot possibly be unlocked without session key

  def login(self, credentials: EmailCredentials):
    self._auth.login(credentials, self.status)
    self.status = self.get_status()
    assert self.is_logged_in

  def logout(self):
    self._auth.logout()
    self.status = self.get_status()
    assert not self.is_logged_in

  def lock(self):
    self._auth.lock()
    self.session_key = None
    self.status = self.get_status()
    assert self.is_locked

  def unlock(self, password: str):
    key = self._auth.unlock(password)
    self.session_key = key
    self.status = self.get_status()
    assert not self.is_locked

  @staticmethod
  def create(conn: CliConnection) -> CliControl:
    return CliControl(
      auth=AuthService(conn),
      import_export=ImportExportService(conn),
      api=ApiService(conn),
      misc=MiscService(conn)
    )
