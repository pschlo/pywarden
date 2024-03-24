
from ..service import Service
from ..cli_responses import DEFAULT_SERVER


class ConfigService(Service):
  def set_server(self, url: str) -> None:
    r = self.conn.run_command(['config', 'server', url])
    if r.returncode > 0:
      raise RuntimeError(f"Failed to set server config")

  def get_server(self) -> str:
    r = self.conn.run_command(['config', 'server'])
    if r.returncode > 0:
      raise RuntimeError(f"Failed to get server config")
    server = r.stdout.decode()
    return server or DEFAULT_SERVER  # a value of None stands for the default server