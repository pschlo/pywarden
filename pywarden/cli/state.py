from pathlib import Path


class CliState:
  cli_path: Path
  session_key: str|None
  data_dir: Path|None

  def __init__(self, cli_path: Path, session_key: str|None = None, data_dir: Path|None = None) -> None:
    self.cli_path = cli_path
    self.session_key = session_key
    self.data_dir = data_dir
