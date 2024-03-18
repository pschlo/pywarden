from __future__ import annotations
from typing import Any
import requests
from requests import Response


type Params = dict[str, Any]
type Body = Any
type Files = dict[str,tuple[str, str|bytes]]


"""
Used by services for communication with Bitwarden Vault Management API
"""
class ApiConnection:
  scheme: str
  host: str
  port: int

  def __init__(self, scheme: str, host: str, port: int) -> None:
    self.scheme = scheme
    self.host = host
    self.port = port

  def _send_request(
      self,
      method: str,
      route: str,
      params: Params|None = None,
      data: Any|None = None,
      json: Any|None = None,
      files: Files|None = None,
  ) -> Response:
    url = f'{self.scheme}://{self.host}:{self.port}{route}'
    resp = requests.request(method, url, params=params, json=json, data=data, files=files)
    if not resp.ok:
      print(f"ERROR ({resp.status_code}): {resp.reason}")
      print(f"{resp.json()}")
    resp.raise_for_status()
    return resp

  def get(
    self,
    route: str,
    params: Params|None = None,
    data: Any|None = None,
    json: Any|None = None,
    files: Files|None = None,
  ) -> Response:
    return self._send_request('GET', route, params=params, data=data, json=json, files=files)
  
  def post(
    self,
    route: str,
    params: Params|None = None,
    data: Any|None = None,
    json: Any|None = None,
    files: Files|None = None,
  ) -> Response:
    return self._send_request('POST', route, params=params, data=data, json=json, files=files)

  def put(
    self,
    route: str,
    params: Params|None = None,
    data: Any|None = None,
    json: Any|None = None,
    files: Files|None = None,
  ) -> Response:
    return self._send_request('PUT', route, params=params, data=data, json=json, files=files)

  def patch(
    self,
    route: str,
    params: Params|None = None,
    data: Any|None = None,
    json: Any|None = None,
    files: Files|None = None,
  ) -> Response:
    return self._send_request('PATCH', route, params=params, data=data, json=json, files=files)

  def delete(
    self,
    route: str,
    params: Params|None = None,
    data: Any|None = None,
    json: Any|None = None,
    files: Files|None = None,
  ) -> Response:
    return self._send_request('DELETE', route, params=params, data=data, json=json, files=files)