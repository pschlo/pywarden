from subprocess import Popen

from ..service import Service


class ApiService(Service):
  def serve(self, port: int, host: str) -> Popen:
    command = ['serve', '--port', str(port), '--hostname', host]
    return self.conn.run_command(command, background=True)
