import secrets
import string

# 16 byte for AES-128 
KEY_LENGTH = 16
_ALPHABET = string.ascii_letters + string.digits


def generate_session_key():
    return "".join(secrets.choice(_ALPHABET) for _ in range(KEY_LENGTH))

def generate_nonce():
    return secrets.randbelow(2**32)

def f(n):
    return n + 1