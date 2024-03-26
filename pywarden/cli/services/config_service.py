
from ..service import Service
from pywarden.constants import DEFAULT_SERVER


class ConfigService(Service):
  def set_server(self, url: str) -> None:
    self.conn.run_command(['config', 'server', url])

  def get_server(self) -> str:
    r = self.conn.run_command(['config', 'server'])
    server = r.stdout.decode()
    return server or DEFAULT_SERVER  # a value of None stands for the default server