import argparse

from common.chat import chat
from common.crypto import decrypt, encrypt
from common.network import connect_to, receive_message, receive_text, send_message, send_text
from common.protocol import build_request, parse_kdc_reply, parse_session_info
from common.utils import KEY_LENGTH, f, generate_nonce, read_key


def request_session_key(kdc_host, kdc_port, id_a, id_b, ka):
    n1 = generate_nonce()
    with connect_to(kdc_host, kdc_port) as sock:
        send_message(sock, build_request(id_a, id_b, n1))
        print(f"sent request: {id_a} -> KDC, asking for {id_b}, N1 = {n1}")
        reply = receive_message(sock)

    for_a, ticket = parse_kdc_reply(reply)
    ks, reply_id_a, reply_id_b, reply_n1 = parse_session_info(decrypt(ka, for_a))
    print(f"received reply: Ks = {ks}")

    if (reply_id_a, reply_id_b, reply_n1) != (id_a, id_b, n1):
        raise ValueError("KDC reply does not match request")
    print("reply valid: IDs and N1 match")
    print(f"received ticket (opaque): {ticket}")
    return ks, ticket


def authenticate_with_peer(peer_host, peer_port, ks, ticket, id_b):
    with connect_to(peer_host, peer_port) as sock:
        send_text(sock, ticket)
        print(f"sent ticket to peer at {peer_host}:{peer_port}")
        n2 = int(decrypt(ks, receive_text(sock)))
        print(f"received challenge: N2 = {n2}")
        send_text(sock, encrypt(ks, str(f(n2))))
        print(f"sent response: f(N2) = {f(n2)}")
        print("handshake sent. type /quit to exit")
        chat(sock, ks, id_b)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--kdc-host", required=True)
    parser.add_argument("--kdc-port", type=int, default=5000)
    parser.add_argument("--id-a", default="Alice")
    parser.add_argument("--id-b", default="Bob")
    parser.add_argument("--peer-host", required=True)
    parser.add_argument("--peer-port", type=int, default=6000)
    args = parser.parse_args()

    ka = read_key(args.id_a)
    while True:
        try:
            parts = input(f"{args.id_a}> ").split()
        except (EOFError, KeyboardInterrupt):
            break
        if not parts:
            continue
        if parts[0] == "quit":
            break
        if parts[0] == "setkey":
            ka = read_key(args.id_a)
        elif parts[0] == "connect":
            id_b = parts[1] if len(parts) > 1 else args.id_b
            try:
                ks, ticket = request_session_key(args.kdc_host, args.kdc_port, args.id_a, id_b, ka)
                authenticate_with_peer(args.peer_host, args.peer_port, ks, ticket, id_b)
            except (OSError, ValueError) as err:
                print(f"failed: {err}")
        else:
            print("commands: connect [id], setkey, quit")


if __name__ == "__main__":
    main()