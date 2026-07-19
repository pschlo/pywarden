from pywarden import SshKeyItem, get_item_type, is_item_type


def test_ssh_key_item_type_is_supported() -> None:
    item = {
        "type": 5,
        "sshKey": {
            "privateKey": "synthetic-private-key",
            "publicKey": "synthetic-public-key",
            "fingerprint": "synthetic-fingerprint",
        },
    }

    assert get_item_type(item) is SshKeyItem  # type: ignore[arg-type]
    assert is_item_type(item, SshKeyItem)  # type: ignore[arg-type]
