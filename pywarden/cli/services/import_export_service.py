
from ..service import Service


class ImportExportService(Service):
  def get_export(self) -> str:
    res = self.conn.run_cli_command(['export', '--format', 'json', '--raw'])
    if res.returncode > 0:
      raise RuntimeError(f"Export failed")
    return res.stdout