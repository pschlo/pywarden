from subprocess import CompletedProcess

import pytest

from pywarden.cli.services.auth_service import AuthService
from pywarden.cli.services.config_service import ConfigService
from pywarden.constants import DEFAULT_SERVER


class FakeConnection:
    def __init__(self, stdout: bytes) -> None:
        self.stdout = stdout
        self.calls: list[tuple[list[str], bytes | None]] = []

    def run_command(self, command, *, input=None):
        self.calls.append((list(command), input))
        return CompletedProcess(command, 0, stdout=self.stdout, stderr=b"")


def test_unlock_strips_session_key() -> None:
    connection = FakeConnection(b"synthetic-session\n")
    service = AuthService(connection)  # type: ignore[arg-type]

    assert service.unlock("master-password") == "synthetic-session"
    assert connection.calls == [(["unlock", "--raw"], b"master-password")]


def test_unlock_rejects_empty_session_key() -> None:
    service = AuthService(FakeConnection(b"\n"))  # type: ignore[arg-type]

    with pytest.raises(RuntimeError, match="empty session key"):
        service.unlock("master-password")


def test_server_output_is_stripped_and_empty_means_default() -> None:
    assert ConfigService(FakeConnection(b"https://example.test\n")).get_server() == (
        "https://example.test"
    )
    assert ConfigService(FakeConnection(b"\n")).get_server() == DEFAULT_SERVER
