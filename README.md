# Pywarden

Typed Python wrapper around the Bitwarden CLI and its local Vault Management
API.

## Requirements

Install the official [Bitwarden CLI](https://bitwarden.com/help/cli/) and make
sure the `bw` executable is available in `PATH`. Pywarden controls that local
executable; uv manages only the Python package and its dependencies.

## Install

Add the current GitHub version to a uv project:

```console
uv add "pywarden @ https://github.com/pschlo/pywarden/archive/refs/heads/main.zip"
```

Without uv, pip also accepts the GitHub reference:

```console
python -m pip install "pywarden @ https://github.com/pschlo/pywarden/archive/refs/heads/main.zip"
```

## Use

Each data directory represents a separate Bitwarden CLI client. Without an
explicit directory, Pywarden uses the CLI's default data directory.

Start with `BaseBwControl`, then use its context managers to obtain logged-in
or unlocked controls. The context managers lock the vault, log out sessions they
created, and stop the local API process when leaving their scope.

```python
from pywarden import BaseBwControl, LoginItem, is_item_type

with BaseBwControl().login_unlock_interactive() as vault:
    for item in vault.get_items():
        print(item["name"])
        if is_item_type(item, LoginItem):
            print(f"  Username: {item['login']['username']}")
```

Pass `CliConfig` or `ApiConfig` to customize the CLI path, data directory,
server, local API hostname, port, and startup timeout.

The local API binds to `localhost` by default. Avoid exposing an unlocked vault
API to other machines.

## Development

```console
uv sync
uv run pytest
uv build
```

The tests use fake API/process objects and temporary subprocesses. They do not
invoke `bw`, prompt for credentials, access a vault, or send network requests.
