import argparse

from common.chat import chat
from common.crypto import decrypt, encrypt
from common.network import create_server, receive_text, send_text
from common.protocol import parse_ticket
from common.utils import f, generate_nonce, read_key


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


def wait_for_session(server, kb):
    print("waiting for a connection (Ctrl+C to go back)")
    try:
        conn, addr = server.accept()
    except KeyboardInterrupt:
        print("\nstopped listening")
        return
    with conn:
        try:
            handle_session(conn, addr, kb)
        except (OSError, ValueError) as err:
            print(f"session failed from {addr[0]}: {err}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=6000)
    args = parser.parse_args()

    kb = read_key("Bob")
    server = create_server(args.host, args.port)
    print(f"Bob listening on {args.host}:{args.port}")
    while True:
        try:
            command = input("Bob> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if command == "quit":
            break
        if command == "setkey":
            kb = read_key("Bob")
        elif command == "listen":
            wait_for_session(server, kb)
        else:
            print("commands: listen, setkey, quit")
    server.close()


if __name__ == "__main__":
    main()