from aes.modes import cbc_decrypt, cbc_encrypt

def encrypt(key, plaintext):
    return cbc_encrypt(key.encode("ascii"), plaintext.encode("ascii")).hex()

def decrypt(key, ciphertext_hex):
    return cbc_decrypt(key.encode("ascii"), bytes.fromhex(ciphertext_hex)).decode("ascii")