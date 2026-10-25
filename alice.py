import argparse
import secrets

from getpass import getpass
from common.network import connect_to, send_message, receive_message
from common.protocol import build_request, parse_kdc_reply, parse_session_info
from common.crypto import decrypt
from common.utils import KEY_LENGTH


def request_session_key(kdc_host, kdc_port, id_a, id_b, ka):
    n1 = secrets.randbelow(2**32)
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


def send_ticket(bob_host, bob_port, ticket):
    with connect_to(bob_host, bob_port) as sock:
        send_message(sock, ticket.encode("ascii"))
        print(f"sent ticket to Bob at {bob_host}:{bob_port}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--kdc-host", required=True)
    parser.add_argument("--kdc-port", type=int, default=5000)
    parser.add_argument("--id-a", default="Alice")
    parser.add_argument("--id-b", default="Bob")
    parser.add_argument("--bob-host", required=True)
    parser.add_argument("--bob-port", type=int, default=5000)
    args = parser.parse_args()

    ka = getpass(f"{args.id_a} master key ({KEY_LENGTH} chars): ")
    try:
        ks, ticket = request_session_key(args.kdc_host, args.kdc_port, args.id_a, args.id_b, ka)
        send_ticket(args.bob_host, args.bob_port, ticket)
    except (ConnectionError, ValueError) as err:
        print(f"failed: {err}")


if __name__ == "__main__":
    main()