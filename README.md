# pywarden
Typed Python wrapper around the Bitwarden CLI and its Vault Management API.

## Installation
This package is not currently uploaded to PyPI. Install as follows:

1. Find your release of choice [here](https://github.com/pschlo/pywarden/releases)
2. Copy the link to `number_conversion-x.x.x.tar.gz`
3. Run `python -m pip install {link}`

You may also prepend a [direct reference](https://peps.python.org/pep-0440/#direct-references), which might be desirable for a `requirements.txt`.


## Building
The `.tar.gz` file in a release is the [source distribution](https://packaging.python.org/en/latest/glossary/#term-Source-Distribution-or-sdist), which was created from the source code with `python3 -m build --sdist`. [Built distributions](https://packaging.python.org/en/latest/glossary/#term-Built-Distribution)
are not provided.


## Examples

Example:

```python
from pywarden import BitwardenControl, CliConfig, ApiConfig, is_item_type, LoginItem

with BitwardenControl(CliConfig(), ApiConfig()).login_unlock_interactive() as ctl:
  for item in ctl.get_items():
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
