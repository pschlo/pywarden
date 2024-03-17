from enum import Enum


class OtpMethod(Enum):
  AUTHENTICATOR = 0
  EMAIL = 1
  YUBIKEY = 3
