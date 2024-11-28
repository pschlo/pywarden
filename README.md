# pywarden
Typed Python wrapper around the Bitwarden CLI and its Vault Management API.

## Installation
This package is not currently uploaded to PyPI. Install as follows:

1. Find your release of choice [here](https://github.com/pschlo/pywarden/releases)
2. Copy the link to `pywarden-x.x.x.tar.gz`
3. Run `python -m pip install {link}`

You may also prepend a [direct reference](https://peps.python.org/pep-0440/#direct-references), which might be desirable for a `requirements.txt`.


## Building
The `.tar.gz` file in a release is the [source distribution](https://packaging.python.org/en/latest/glossary/#term-Source-Distribution-or-sdist), which was created from the source code with `python3 -m build --sdist`. [Built distributions](https://packaging.python.org/en/latest/glossary/#term-Built-Distribution)
are not provided.



## Introduction

Each data directory represents a different Bitwarden client. When no data directory is specified, the default Bitwarden CLI directory is used.

There are three basic classes to control a Bitwarden client. Each represents a view on the Bitwarden client with a certain permission level:

* `BaseBwControl`: unauthenticated view of the Bitwarden client. Has several methods that can be used in a `with` statement to obtain `LoggedInBwControl` or `UnlockedBwControl` objects.
* `LoggedInBwControl`: authenticated, but locked view of the Bitwarden client. Has several methods that can be used in a `with` statement to obtain an `UnlockedBwControl`.
* `UnlockedBwControl`: authenticated and unlocked view of Bitwarden client.

It is perfectly valid to use a control with less permission than the client, but using a control with more permission is invalid will fail eventually. You should always start with a `BaseBwControl` (least permissions), and use its context manager methods to get more permissive control objects. Dependent on which context manager is used, they will ensure that the client is locked and logged out, and that the API process is stopped. You can pass `CliConfig` and `ApiConfig` instances to `BaseBwControl` to customize its behaviour (e.g. use a different client/data directory). Make sure to specify the path to your Bitwarden CLI executable if it is not named `bw` and in `PATH`.


## Examples

Example:

```python
from pywarden import BaseBwControl, is_item_type, LoginItem

with BaseBwControl().login_unlock_interactive() as bw:
  for item in bw.get_items():
    print(item['name'])
    if is_item_type(item, LoginItem):
      print(f"  Username: {item['login']['username']}")
      print(f"  Password: {item['login']['password']}")
```

This will:

* prompt the user for their login/unlock data
* if necessary, log into Bitwarden account
* unlock vault
* print all item names
* for each login item, also print username and password
* lock the vault
* if we had to log in previously, log back out
