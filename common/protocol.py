SEP = "||"

def build_request(id_a, id_b, n1):
    return SEP.join([id_a, id_b, str(n1)]).encode("ascii")

def parse_request(data):
    id_a, id_b, n1 = data.decode("ascii").split(SEP)
    return id_a, id_b, int(n1)

def build_ticket(ks, id_a):
    return SEP.join([ks, id_a])

def parse_ticket(text):
    ks, id_a = text.split(SEP)
    return ks, id_a

def build_kdc_reply(ks, id_a, id_b, n1, ticket):
    return SEP.join([ks, id_a, id_b, str(n1), ticket]).encode("ascii")

def parse_kdc_reply(data):
    ks, id_a, id_b, n1, ticket = data.decode("ascii").split(SEP, 4)
    return ks, id_a, id_b, int(n1), ticket