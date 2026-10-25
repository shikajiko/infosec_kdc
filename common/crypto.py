def encrypt(key, plaintext):
    k = key.encode("ascii")
    data = plaintext.encode("ascii")
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(data)).hex()


def decrypt(key, ciphertext_hex):
    k = key.encode("ascii")
    data = bytes.fromhex(ciphertext_hex)
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(data)).decode("ascii")