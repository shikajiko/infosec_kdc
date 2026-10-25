import argparse

from getpass import getpass
from common.network import create_server, receive_message, send_message
from common.protocol import parse_request, build_kdc_reply, build_ticket, build_session_info
from common.utils import generate_session_key, KEY_LENGTH
from common.crypto import encrypt
from kdc_core.key_store import KeyStore

def handle_request(conn, addr, store):
    data = receive_message(conn)
    id_a, id_b, n1 = parse_request(data)
    print(f"[{addr[0]}:{addr[1]}] request from {id_a} for {id_b}, N1 = {n1}")
    if not (store.has_entity(id_a) and store.has_entity(id_b)):
        raise ValueError("unknown entity")

    ks = generate_session_key()
    for_a = encrypt(store.get_key(id_a), build_session_info(ks, id_a, id_b, n1))
    ticket = encrypt(store.get_key(id_b), build_ticket(ks, id_a))
    send_message(conn, build_kdc_reply(for_a, ticket))
    print(f"reply sent to {id_a}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=5000)
    args = parser.parse_args()
    store = KeyStore()
    for entity_id in ("Alice", "Bob"):
        while True:
            try:
                store.set_key(entity_id, getpass(f"key for {entity_id} ({KEY_LENGTH} chars): "))
                break
            except ValueError as err:
                print(err)

    server = create_server(args.host, args.port)
    print(f"KDC listening on {args.host}:{args.port}")
    while True:
        conn, addr = server.accept()
        with conn:
            try:
                handle_request(conn, addr, store)
                
            except (ConnectionError, ValueError) as err:
                print(f"bad request from {addr[0]}: {err}")


if __name__ == "__main__":
    main()