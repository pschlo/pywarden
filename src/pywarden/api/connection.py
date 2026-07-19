from __future__ import annotations
from typing import Any
import requests
from requests import Response
import logging

from .state import ApiState


log = logging.getLogger(__name__)

Params = dict[str, Any]
Body = Any
Files = dict[str, tuple[str, str | bytes]]


class ApiConnection:
    state: ApiState

    def __init__(
        self, state: ApiState, session: requests.Session | None = None, timeout_secs: float = 30
    ) -> None:
        if timeout_secs <= 0:
            raise ValueError("API request timeout must be positive")
        self.state = state
        self.session = session or requests.Session()
        self.timeout_secs = timeout_secs

    def _send_request(
        self,
        method: str,
        route: str,
        params: Params | None = None,
        data: Any | None = None,
        json: Any | None = None,
        files: Files | None = None,
    ) -> Response:
        url = f"{self.state.scheme}://{self.state.host}:{self.state.port}{route}"
        resp = self.session.request(
            method,
            url,
            params=params,
            json=json,
            data=data,
            files=files,
            timeout=self.timeout_secs,
        )
        if not resp.ok:
            log.error(f"ERROR ({resp.status_code}): {resp.reason}")
        resp.raise_for_status()
        return resp

    def get(
        self,
        route: str,
        params: Params | None = None,
        data: Any | None = None,
        json: Any | None = None,
        files: Files | None = None,
    ) -> Response:
        return self._send_request("GET", route, params=params, data=data, json=json, files=files)

    def post(
        self,
        route: str,
        params: Params | None = None,
        data: Any | None = None,
        json: Any | None = None,
        files: Files | None = None,
    ) -> Response:
        return self._send_request("POST", route, params=params, data=data, json=json, files=files)

    def put(
        self,
        route: str,
        params: Params | None = None,
        data: Any | None = None,
        json: Any | None = None,
        files: Files | None = None,
    ) -> Response:
        return self._send_request("PUT", route, params=params, data=data, json=json, files=files)

    def patch(
        self,
        route: str,
        params: Params | None = None,
        data: Any | None = None,
        json: Any | None = None,
        files: Files | None = None,
    ) -> Response:
        return self._send_request("PATCH", route, params=params, data=data, json=json, files=files)

    def delete(
        self,
        route: str,
        params: Params | None = None,
        data: Any | None = None,
        json: Any | None = None,
        files: Files | None = None,
    ) -> Response:
        return self._send_request("DELETE", route, params=params, data=data, json=json, files=files)
