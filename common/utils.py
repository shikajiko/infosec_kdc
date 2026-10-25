import secrets
import string

KEY_LENGTH = 16
_ALPHABET = string.ascii_letters + string.digits


def generate_session_key():
    return "".join(secrets.choice(_ALPHABET) for _ in range(KEY_LENGTH))