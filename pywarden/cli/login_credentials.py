from __future__ import annotations
from enum import Enum
from typing import TypedDict
from getpass import getpass


class EmailCredentials(TypedDict):
  email: str
  password: str
  two_step_credentials: TwoStepCredentials|None


class TwoStepCredentials(TypedDict):
  type: TwoStepType
  code: str

class TwoStepType(Enum):
  AUTHENTICATOR = 0
  EMAIL = 1
  YUBIKEY = 3



def ask_email_credentials() -> EmailCredentials:
  r = None
  while (r is None) or not len(r) > 0:
    r = input("Email: ").strip()
  email = r
  
  r = None
  while (r is None) or not len(r) > 0:
    r = getpass("Password [input hidden]: ")
  password = r

  r = None
  while (r is None) or r not in {'y', 'n'}:
    r = input("Two-step login? [y/n] ").strip().lower()
  is_two_step = r == 'y'


  two_step_creds: TwoStepCredentials|None

  if is_two_step:
    r = None
    while (r is None) or r not in {'0', '1', '3'}:
      r = input("2FA method (0: Authenticator, 1: Email, 3: YubiKey OTP): ").strip()
    two_step_type = TwoStepType(int(r))

    r = None
    while (r is None) or not len(r) > 0:
      r = input("2FA code: ").strip()
    two_step_code = r

    two_step_creds = {'type': two_step_type, 'code': two_step_code}
  else:
    two_step_creds = None
  
  return {
    "email": email,
    "password": password,
    "two_step_credentials": two_step_creds
  }
