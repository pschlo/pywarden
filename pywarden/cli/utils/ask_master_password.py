from __future__ import annotations
from getpass import getpass


def ask_master_password() -> str:
  r = None
  while (r is None) or not len(r) > 0:
    r = getpass("Master Password [input hidden]: ")
  return r