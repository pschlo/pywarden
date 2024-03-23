
from ..service import Service


class ConfigService(Service):
  def set_server(self, url: str) -> None:
    r = self.conn.run_command(['config', 'server', url])
    if r.returncode > 0:
      raise RuntimeError(f"Failed to set config")
