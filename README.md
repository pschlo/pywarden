# pywarden
Typed Python wrapper around the Bitwarden CLI and its Vault Management API.



Example:

```python
creds: EmailCredentials = {
  'email': 'foo@bar.com',
  'password': 'mypassword123',
  'two_step_credentials': None
}

with BitwardenControl.create(
  api_config = ApiConfig(),
  cli_config = CliConfig(),
  credentials = creds,
  master_password = creds['password']
) as control:
  
  items = control.api.get_items()['data']['data']
  for item in items:
    print(item['name'])
```

