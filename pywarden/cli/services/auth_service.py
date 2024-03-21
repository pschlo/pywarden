from typing import Any, cast

from ..service import Service
from ..login_credentials import LoginCredentials
from ..cli_responses import StatusResponse, AuthenticatedStatusResponse


class AuthService(Service):
  
  def login(self, credentials: LoginCredentials, status: StatusResponse) -> None:

    if status['status'] == 'unauthenticated':
      print("Status: Not logged in")
      print(f"Logging in as {credentials['email']}")
      command = ['login', credentials['email'], credentials['password']]
      r = self.conn.run_cli_command(command)
      if r.returncode > 0:
        raise RuntimeError(f"Login failed")

    else:
      status = cast(AuthenticatedStatusResponse, status)
      print(f"Status: Logged in as {status['userEmail']}")
      # The emails should match. Otherwise, log out and back in
      if status['userEmail'] != credentials['email']:
        print(f"Should be using account '{credentials['email']}', logging out and back in")
        self.logout()
        new_status: StatusResponse = {
          'lastSync': status['lastSync'],
          'serverUrl': status['serverUrl'],
          'status': 'unauthenticated'
        }
        self.login(credentials, new_status)
      
    
  def logout(self) -> None:
    if self.conn.run_cli_command(['logout']).returncode > 0:
      raise RuntimeError(f"Logout failed")
    
  def lock(self) -> None:
    r = self.conn.run_cli_command(['lock'])
    if r.returncode > 0:
      raise RuntimeError(f"Lock failed")

  def unlock(self, password: str) -> str:
    if not password:
      raise RuntimeError(f"Empty master password")
    r = self.conn.run_cli_command(['unlock', '--raw', password])
    if r.returncode > 0:
      raise RuntimeError(f"Unlock failed")
    return r.stdout
