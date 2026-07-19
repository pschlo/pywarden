from pathlib import Path
import subprocess
import sys

import pytest

from pywarden.cli.connection import CliCommandError, CliConnection
from pywarden.cli.state import CliState


def test_cli_connection_passes_session_and_data_directory(tmp_path: Path) -> None:
    connection = CliConnection(
        CliState(
            cli_path=Path(sys.executable),
            session_key="synthetic-session",
            data_dir=tmp_path,
        )
    )

    environment = connection.get_env()

    assert environment["BW_SESSION"] == "synthetic-session"
    assert environment["BITWARDENCLI_APPDATA_DIR"] == str(tmp_path)


def test_cli_connection_runs_a_temporary_subprocess() -> None:
    connection = CliConnection(CliState(cli_path=Path(sys.executable)))

    result = connection.run_command(["-c", "print('synthetic output')"])

    assert result.stdout.decode().strip() == "synthetic output"


def test_cli_failure_without_stderr_is_not_masked_by_index_error() -> None:
    connection = CliConnection(CliState(cli_path=Path(sys.executable)))

    with pytest.raises(CliCommandError, match="exited with status 7") as error:
        connection.run_command(["-c", "raise SystemExit(7)"])

    assert error.value.returncode == 7
    assert not isinstance(error.value, subprocess.CalledProcessError)
