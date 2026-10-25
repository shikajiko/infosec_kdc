import argparse
from getpass import getpass

from common.crypto import encrypt, decrypt
from common.network import create_server, receive_text, send_text
from common.protocol import parse_ticket
from common.utils import KEY_LENGTH, generate_nonce, f
from common.chat import chat

def handle_session(conn, addr, kb):
    ticket = receive_text(conn)
    print(f"[{addr[0]}:{addr[1]}] received ticket: {ticket}")
    ks, id_a = parse_ticket(decrypt(kb, ticket))
    print(f"ticket valid: session with {id_a}, Ks = {ks}")

    n2 = generate_nonce()
    send_text(conn, encrypt(ks, str(n2)))
    print(f"sent challenge: N2 = {n2}")

    answer = int(decrypt(ks, receive_text(conn)))
    if answer != f(n2):
        raise ValueError("wrong answer to challenge")
    print(f"{id_a} authenticated. type /quit to exit")
    chat(conn, ks, id_a)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=5000)
    args = parser.parse_args()

    kb = getpass(f"Bob master key ({KEY_LENGTH} chars): ")
    server = create_server(args.host, args.port)
    print(f"Bob listening on {args.host}:{args.port}")
    while True:
        conn, addr = server.accept()
        with conn:
            try:
                handle_session(conn, addr, kb)
            except (ConnectionError, ValueError) as err:
                print(f"session failed from {addr[0]}: {err}")


if __name__ == "__main__":
    main()