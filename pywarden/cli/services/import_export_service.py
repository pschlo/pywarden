
from ..service import Service


class ImportExportService(Service):
  def get_export(self) -> str:
    r = self.conn.run_command(['export', '--format', 'json', '--raw'])
    return r.stdout.decode()