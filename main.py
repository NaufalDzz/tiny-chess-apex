import http.client, json, os, sys, urllib.parse

URL = os.environ.get("MAKEFUN_ENV_URL") or sys.exit("MAKEFUN_ENV_URL is not set")
u = urllib.parse.urlparse(URL)
VALUE = {"p": 1, "n": 3, "b": 3, "r": 5, "q": 9, "k": 100}

def post(path, body):
    c = http.client.HTTPConnection(u.hostname, u.port or 80, timeout=30)
    c.request("POST", path, json.dumps(body), {"content-type": "application/json"})
    r = c.getresponse()
    data = json.loads(r.read())
    c.close()
    if r.status >= 400:
        sys.exit(f"{path}: HTTP {r.status} {data}")
    return data

def board_of(fen):
    b = {}
    for i, row in enumerate(fen.split()[0].split("/")):
        f = 0
        for ch in row:
            if ch.isdigit():
                f += int(ch)
            else:
                b["abcdefgh"[f] + str(8 - i)] = ch
                f += 1
    return b

def choose(g):
    b = board_of(g["fen"])
    def rank(m):
        mv = b[m[:2]].lower()
        vc = b.get(m[2:4])
        if vc is None and mv == "p" and m[0] != m[2]:
            vc = "p"
        return (-(VALUE[vc.lower()] if vc else 0), -(VALUE[m[4]] if len(m) == 5 else 0), VALUE[mv], m)
    return min(g["legal_moves"], key=rank)

while True:
    g = post("/game", {})
    if g["status"] == "done":
        break
    while g["status"] == "your_move":
        g = post("/move", {"game": g["game"], "move": choose(g)})
