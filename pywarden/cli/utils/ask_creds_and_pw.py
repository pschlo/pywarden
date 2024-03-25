from __future__ import annotations
from .ask_login_credentials import ask_email_credentials
from .ask_master_password import ask_master_password
from ..control import CliControl
from ..cli_responses import AuthStatusResponse, StatusResponse
from ..login_credentials import EmailCredentials

from typing import cast


def ask_creds_and_pw(cli: CliControl, email: str|None = None) -> tuple[EmailCredentials|None, str]:
  status = cli.get_status()

  if cli.is_logged_in(status) and cast(AuthStatusResponse, status)['userEmail'] == email:
    creds = None
    master_password = ask_master_password()
  else:
    if email is not None:
      print(f"Logging in as {email}")
    creds = ask_email_credentials(email)
    # login(creds)
    master_password = creds['password']
  
  return creds, master_password
