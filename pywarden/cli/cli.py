from __future__ import annotations
from .services import AuthService, ImportExportService, MiscService, ApiService
from .connection import CliConnection


class Cli:
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
    self.login = self._auth.login
    self.logout = self._auth.logout
    self.lock = self._auth.lock
    self.unlock = self._auth.unlock

    self.get_export = self._import_export.get_export

    self.serve_api = self._api.serve

    self.get_status = self._misc.get_status


  @staticmethod
  def create(conn: CliConnection) -> Cli:
    return Cli(
      auth=AuthService(conn),
      import_export=ImportExportService(conn),
      api=ApiService(conn),
      misc=MiscService(conn)
    )



