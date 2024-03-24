from typing import Any, cast

from ..service import Service
from ..login_credentials import EmailCredentials
from ..cli_responses import StatusResponse, AuthenticatedStatusResponse


class AuthService(Service):

  def login(self, creds: EmailCredentials) -> None:  
    command = ['login', creds['email']]
    two_step_creds = creds['two_step_credentials']
    if two_step_creds is not None:
      command += ['--method', str(two_step_creds['type'].value), '--code', two_step_creds['code']]

    r = self.conn.run_command(command, input=creds['password'].encode())
    if r.returncode > 0:
      raise RuntimeError(f"Login failed")
    
  def logout(self) -> None:
    if self.conn.run_command(['logout']).returncode > 0:
      raise RuntimeError(f"Logout failed")
    
  def lock(self) -> None:
    r = self.conn.run_command(['lock'])
    if r.returncode > 0:
      raise RuntimeError(f"Lock failed")

  def unlock(self, password: str) -> str:
    if not password:
      raise RuntimeError(f"Empty master password")
    r = self.conn.run_command(['unlock', '--raw'], input=password.encode())
    if r.returncode > 0:
      raise RuntimeError(f"Unlock failed")
    return r.stdout.decode()
