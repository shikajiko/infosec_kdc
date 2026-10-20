SEP = "||"

def build_request(id_a, id_b, n1):
    return SEP.join([id_a, id_b, str(n1)]).encode("ascii")


def parse_request(data):
    id_a, id_b, n1 = data.decode("ascii").split(SEP)
    return id_a, id_b, int(n1)