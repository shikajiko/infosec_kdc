import socket
import threading

from common.crypto import decrypt, encrypt
from common.network import receive_text, send_text


def _listen(sock, key, peer, done):
    try:
        while True:
            cipher = receive_text(sock)
            print(f"\nreceived ciphertext: {cipher}")
            print(f"{peer}: {decrypt(key, cipher)}")
    except (OSError, ValueError):
        if not done.is_set():
            print("\nconnection closed, press Enter to exit")
    finally:
        done.set()


def chat(sock, key, peer):
    done = threading.Event()
    threading.Thread(target=_listen, args=(sock, key, peer, done), daemon=True).start()
    try:
        while not done.is_set():
            line = input()
            if line == "/quit" or done.is_set():
                break
            try:
                cipher = encrypt(key, line)
            except UnicodeEncodeError:
                print("ASCII characters only")
                continue
            print(f"sent ciphertext: {cipher}")
            send_text(sock, cipher)
    except (EOFError, KeyboardInterrupt, OSError):
        pass
    finally:
        done.set()
        try:
            sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass