from subprocess import TimeoutExpired
from typing import Any

import pytest
import requests

from pywarden.api.connection import ApiConnection
from pywarden.api.control import ApiControl
from pywarden.api.state import ApiState


class FakeResponse:
    ok = True
    status_code = 200
    reason = "OK"

    def raise_for_status(self) -> None:
        return None


class FakeSession:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    def request(self, method: str, url: str, **kwargs: Any) -> FakeResponse:
        self.calls.append({"method": method, "url": url, **kwargs})
        return FakeResponse()


class StubbornProcess:
    def __init__(self) -> None:
        self.terminated = False
        self.killed = False
        self.wait_calls: list[float | None] = []

    def terminate(self) -> None:
        self.terminated = True

    def kill(self) -> None:
        self.killed = True

    def wait(self, timeout: float | None = None) -> int:
        self.wait_calls.append(timeout)
        if len(self.wait_calls) == 1:
            raise TimeoutExpired("bw serve", timeout)
        return 0


def test_api_connection_uses_configured_timeout() -> None:
    session = FakeSession()
    connection = ApiConnection(
        ApiState("localhost", 8087),
        session=session,  # type: ignore[arg-type]
        timeout_secs=2.5,
    )

    connection.get("/status")

    assert session.calls == [
        {
            "method": "GET",
            "url": "http://localhost:8087/status",
            "params": None,
            "json": None,
            "data": None,
            "files": None,
            "timeout": 2.5,
        }
    ]


def test_api_connection_rejects_non_positive_timeout() -> None:
    with pytest.raises(ValueError, match="positive"):
        ApiConnection(ApiState("localhost", 8087), timeout_secs=0)


def test_shutdown_kills_server_that_ignores_terminate() -> None:
    process = StubbornProcess()
    control = object.__new__(ApiControl)
    control.process = process  # type: ignore[assignment]

    with pytest.raises(TimeoutError, match="did not exit"):
        control.shutdown(1)

    assert process.terminated
    assert process.killed
    assert process.wait_calls == [1, None]


def test_api_reachability_treats_any_request_failure_as_unreachable() -> None:
    control = object.__new__(ApiControl)

    def status() -> None:
        raise requests.Timeout("synthetic timeout")

    control.status = status  # type: ignore[method-assign]

    assert not control.is_reachable()
