

from ..service import Service


class AuthService(Service):
  def login(self, email: str, password: str) -> None:
    if self.conn.run_cli_command(['login', email, password]).returncode > 0:
      raise RuntimeError(f"Login failed")
    self.conn.is_logged_in = True
    
  def logout(self) -> None:
    if self.conn.run_cli_command(['logout']).returncode > 0:
      raise RuntimeError(f"Logout failed")
    self.conn.is_logged_in = False
    
  def lock(self) -> None:
    r = self.conn.run_cli_command(['lock'])
    if r.returncode > 0:
      raise RuntimeError(f"Lock failed")
    self.conn.session_key = None

  def unlock(self, password: str) -> None:
    if not password:
      raise RuntimeError(f"Empty master password")
    r = self.conn.run_cli_command(['unlock', '--raw', password])
    if r.returncode > 0:
      raise RuntimeError(f"Unlock failed")
    self.conn.session_key = r.stdout