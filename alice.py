import argparse
import secrets

from common.network import connect_to, send_message, receive_message
from common.protocol import build_request, parse_kdc_reply

def request_session_key(kdc_host, kdc_port, id_a, id_b):
    n1 = secrets.randbelow(2**32)
    with connect_to(kdc_host, kdc_port) as sock:
        send_message(sock, build_request(id_a, id_b, n1))
        print(f"sent request: {id_a} -> KDC, asking for {id_b}, N1 = {n1}")
        reply = receive_message(sock)

    ks, reply_id_a, reply_id_b, reply_n1, ticket = parse_kdc_reply(reply)
    print(f"received reply: Ks = {ks}")

    if (reply_id_a, reply_id_b, reply_n1) != (id_a, id_b, n1):
        raise ValueError("KDC reply does not match request")
    print("reply valid: IDs and N1 match")
    print(f"received ticket: {ticket}")
    return ks, ticket


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--kdc-host", required=True)
    parser.add_argument("--kdc-port", type=int, default=5000)
    parser.add_argument("--id-a", default="Alice")
    parser.add_argument("--id-b", default="Bob")
    args = parser.parse_args()

    try:
        ks, ticket = request_session_key(args.kdc_host, args.kdc_port, args.id_a, args.id_b)
    except (ConnectionError, ValueError) as err:
        print(f"KDC exchange failed: {err}")


if __name__ == "__main__":
    main()