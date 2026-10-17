import http.server, os, urllib.parse
D="/private/tmp/claude-501/-Users-jakeschantz/13d06805-9b09-406f-b090-40551ef08dda/scratchpad/guide"
class H(http.server.SimpleHTTPRequestHandler):
    def __init__(s,*a,**k): super().__init__(*a,directory=D,**k)
    def do_GET(s):
        u=urllib.parse.urlparse(s.path)
        if u.path=="/set":
            q=urllib.parse.parse_qs(u.query); p=q.get("p",[""])[0]
            if p.isdigit(): open(os.path.join(D,"current"),"w").write(p)
            s.send_response(204); s.end_headers(); return
        return super().do_GET()
    def log_message(s,*a): pass
http.server.ThreadingHTTPServer(("127.0.0.1",8791),H).serve_forever()
