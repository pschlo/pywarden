import json

from ..cli_responses import StatusResponse
from ..service import Service


class MiscService(Service):
  def get_status(self) -> StatusResponse:
    return json.loads(self.conn.run_command(['status']).stdout)