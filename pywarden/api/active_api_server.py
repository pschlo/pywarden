from __future__ import annotations
from subprocess import Popen
import subprocess
import json
from pathlib import Path
from typing import Any, ContextManager, TypedDict, Literal, cast
from collections.abc import Sequence
import time
import requests
from requests import Response
import math


SCHEME = 'http'
HOST = 'localhost'
TIMEOUT_SECS = 10

type Params = dict[str, Any]
type Body = Any
type Files = dict[str,tuple[str, str|bytes]]


class ActiveApiServer:
  process: Popen
  port: int
  hostname: str | None

  def __init__(self, process: Popen, port: int, hostname: str|None = None) -> None:
    self.process = process
    self.port = port
    self.hostname = hostname


  def wait_until_ready(self):
    success = False
    t0 = time.perf_counter()
    
    while time.perf_counter() - t0 < TIMEOUT_SECS:
      try:
        self.get('/status')
        success = True
        break
      except requests.ConnectionError:
        pass
      except requests.RequestException:
        break
      time.sleep(0.1)

    if not success:
      self.stop()
      raise TimeoutError(f"API server failed to start after {TIMEOUT_SECS} seconds")


  def stop(self):
    print(f"Shutting down API server")
    self.process.terminate()


  def _send_request(
    self,
    method: str,
    route: str,
    params: Params|None = None,
    data: Any|None = None,
    json: Any|None = None,
    files: Files|None = None,
  ) -> Response:
    url = f'{SCHEME}://{HOST}:{self.port}{route}'
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
