from __future__ import annotations
from getpass import getpass


def ask_master_password(email: str|None = None) -> str:
  r = None
  while (r is None) or not len(r) > 0:
    r = getpass(f"Master Password {f'for {email} ' if email is not None else ''}[input hidden]: ")
  return r
