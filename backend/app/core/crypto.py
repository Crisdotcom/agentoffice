"""Encryption at rest for provider API keys."""

from cryptography.fernet import Fernet, InvalidToken


class KeyVault:
    def __init__(self, master_key: str) -> None:
        try:
            self._fernet = Fernet(master_key.encode())
        except (ValueError, TypeError) as exc:
            raise ValueError(
                "AGENTOFFICE_SECRET_KEY must be a Fernet key (see .env.example to generate one)"
            ) from exc

    def encrypt(self, plaintext: str) -> str:
        return self._fernet.encrypt(plaintext.encode()).decode()

    def decrypt(self, token: str) -> str:
        try:
            return self._fernet.decrypt(token.encode()).decode()
        except InvalidToken as exc:
            raise ValueError("Stored key cannot be decrypted with the current secret key") from exc


def mask(api_key: str) -> str:
    """Safe representation for the UI: never return the full key."""
    return f"{api_key[:4]}…{api_key[-4:]}" if len(api_key) > 12 else "••••"
