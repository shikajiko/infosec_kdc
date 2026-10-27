import socket
import threading

from common.crypto import decrypt, encrypt
from common.network import receive_text, send_text


def _listen(sock, key, peer, done):
    try:
        while True:
            print(f"\n{peer}: {decrypt(key, receive_text(sock))}")
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
                send_text(sock, encrypt(key, line))
            except UnicodeEncodeError:
                print("ASCII characters only")
    except (EOFError, KeyboardInterrupt, OSError):
        pass
    finally:
        done.set()
        try:
            sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass