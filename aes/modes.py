import secrets

from aes.core import decrypt_block, encrypt_block, expand_key

BLOCK = 16


def pad(data):
    n = BLOCK - len(data) % BLOCK
    return data + bytes([n]) * n


def unpad(data):
    if not data or len(data) % BLOCK:
        raise ValueError("invalid padded length")
    n = data[-1]
    if n < 1 or n > BLOCK or data[-n:] != bytes([n]) * n:
        raise ValueError("invalid padding")
    return data[:-n]


def _xor(a, b):
    return bytes(x ^ y for x, y in zip(a, b))


def cbc_encrypt(key, plaintext, iv=None):
    round_keys = expand_key(key)
    iv = iv or secrets.token_bytes(BLOCK)
    data = pad(plaintext)
    previous = iv
    out = [iv]
    for i in range(0, len(data), BLOCK):
        previous = encrypt_block(_xor(data[i:i + BLOCK], previous), round_keys)
        out.append(previous)
    return b"".join(out)


def cbc_decrypt(key, data):
    if len(data) < 2 * BLOCK or len(data) % BLOCK:
        raise ValueError("invalid ciphertext length")
    round_keys = expand_key(key)
    previous = data[:BLOCK]
    out = []
    for i in range(BLOCK, len(data), BLOCK):
        block = data[i:i + BLOCK]
        out.append(_xor(decrypt_block(block, round_keys), previous))
        previous = block
    return unpad(b"".join(out))