from typing import Any, cast

from ..service import Service
from ...login_credentials import EmailCredentials


class AuthService(Service):

  def login(self, creds: EmailCredentials) -> None:  
    command = ['login', creds['email']]
    two_step_creds = creds['two_step_credentials']
    if two_step_creds is not None:
      command += ['--method', str(two_step_creds['type'].value), '--code', two_step_creds['code']]

    self.conn.run_command(command, input=creds['password'].encode())
    
  def logout(self) -> None:
    self.conn.run_command(['logout'])
    
  def lock(self) -> None:
    self.conn.run_command(['lock'])

  def unlock(self, password: str) -> str:
    if not password:
      raise RuntimeError(f"Empty master password")
    r = self.conn.run_command(['unlock', '--raw'], input=password.encode())
    return r.stdout.decode()
