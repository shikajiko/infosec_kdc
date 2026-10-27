import secrets
import string
from getpass import getpass

# 16 byte for AES-128 
KEY_LENGTH = 16
_ALPHABET = string.ascii_letters + string.digits

def generate_session_key():
    return "".join(secrets.choice(_ALPHABET) for _ in range(KEY_LENGTH))

def generate_nonce():
    return secrets.randbelow(2**32)

def f(n):
    return n + 1

def read_key(label):
    while True:
        key = getpass(f"{label} master key ({KEY_LENGTH} chars): ")
        if len(key) == KEY_LENGTH and key.isascii():
            return key
        print(f"key must be {KEY_LENGTH} ASCII characters")