import pytest
from cryptography.fernet import Fernet

from app.core.crypto import KeyVault, mask


def test_round_trip():
    vault = KeyVault(Fernet.generate_key().decode())
    token = vault.encrypt("sk-secret-123")
    assert token != "sk-secret-123"
    assert vault.decrypt(token) == "sk-secret-123"


def test_wrong_key_fails():
    token = KeyVault(Fernet.generate_key().decode()).encrypt("x")
    with pytest.raises(ValueError):
        KeyVault(Fernet.generate_key().decode()).decrypt(token)


def test_invalid_master_key():
    with pytest.raises(ValueError):
        KeyVault("change-me")


def test_mask_never_leaks_short_keys():
    assert mask("short") == "••••"
    assert mask("sk-ant-1234567890abcd") == "sk-a…abcd"
