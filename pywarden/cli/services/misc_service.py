import json

from ..cli_responses import StatusResponse, DEFAULT_SERVER
from ..service import Service


class MiscService(Service):
  def get_status(self) -> StatusResponse:
    r =  json.loads(self.conn.run_command(['status']).stdout)
    # fix serverUrl of None
    if 'serverUrl' in r and r['serverUrl'] is None:
      r['serverUrl'] = DEFAULT_SERVER
    return r