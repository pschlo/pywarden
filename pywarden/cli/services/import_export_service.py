
from ..service import Service


class ImportExportService(Service):
  def get_export(self) -> str:
    r = self.conn.run_command(['export', '--format', 'json', '--raw'])
    data = r.stdout.decode().strip()
    if not data:
      raise RuntimeError(f"Export failed")
    return data
