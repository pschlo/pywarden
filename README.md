# pywarden
Typed Python wrapper around the Bitwarden CLI and its Vault Management API.



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
