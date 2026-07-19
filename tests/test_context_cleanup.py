import pytest

from pywarden.bitwarden_control import base_control
from pywarden.bitwarden_control.base_control import BaseBwControl


class FakeCli:
    cli_path = None
    data_dir = None

    def __init__(self) -> None:
        self.logged_out = False

    def status(self):
        return {"status": "unauthenticated", "serverUrl": "https://bitwarden.com"}

    def get_server(self) -> str:
        return "https://bitwarden.com"

    def login(self, credentials, status) -> None:
        return None

    def logout(self) -> None:
        self.logged_out = True


class FakeLoggedInControl:
    def __init__(self, cli: FakeCli, api) -> None:
        self.cli = cli

    def stop_api(self) -> None:
        raise RuntimeError("synthetic shutdown failure")

    def logout(self) -> None:
        self.cli.logout()


def test_login_context_logs_out_even_when_api_shutdown_fails(monkeypatch) -> None:
    cli = FakeCli()
    monkeypatch.setattr(base_control, "LoggedInBwControl", FakeLoggedInControl)
    control = BaseBwControl(cli=cli)  # type: ignore[arg-type]
    credentials = {
        "email": "synthetic@example.test",
        "password": "synthetic-password",
        "two_step_credentials": None,
    }

    with pytest.raises(RuntimeError, match="shutdown failure"):
        with control.login(credentials):  # type: ignore[arg-type]
            pass

    assert cli.logged_out
