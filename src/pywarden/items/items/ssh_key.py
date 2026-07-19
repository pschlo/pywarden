from __future__ import annotations
from typing import TypedDict

from ..item import Item


class SshKeyItem(Item):
    sshKey: SshKeyData


class SshKeyData(TypedDict):
    privateKey: str
    publicKey: str
    fingerprint: str
