import argparse
import threading

from common.crypto import encrypt
from common.network import create_server, receive_message, send_message
from common.protocol import build_kdc_reply, build_session_info, build_ticket, parse_request
from common.utils import KEY_LENGTH, generate_session_key
from kdc_core.key_store import KeyStore


def prompt_key(store, entity_id):
    try:
        store.set_key(entity_id, input(f"key for {entity_id} ({KEY_LENGTH} chars): "))
    except ValueError as err:
        print(err)
        return False
    return True


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


def serve(server, store):
    while True:
        conn, addr = server.accept()
        with conn:
            try:
                handle_request(conn, addr, store)
            except (ConnectionError, ValueError) as err:
                print(f"bad request from {addr[0]}: {err}")


def command_loop(store):
    while True:
        try:
            parts = input("kdc> ").split()
        except (EOFError, KeyboardInterrupt):
            return
        if not parts:
            continue
        if parts[0] == "quit":
            return
        if parts[0] == "listkeys":
            print(", ".join(store.list_entities()) or "(none)")
        elif parts[0] == "setkey" and len(parts) == 2:
            if prompt_key(store, parts[1]):
                print(f"key set for {parts[1]}")
        else:
            print("commands: setkey <id>, listkeys, quit")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=5000)
    args = parser.parse_args()

    store = KeyStore()
    for entity_id in ("Alice", "Bob"):
        while not prompt_key(store, entity_id):
            pass

    server = create_server(args.host, args.port)
    print(f"KDC listening on {args.host}:{args.port}")
    threading.Thread(target=serve, args=(server, store), daemon=True).start()
    command_loop(store)


if __name__ == "__main__":
    main()