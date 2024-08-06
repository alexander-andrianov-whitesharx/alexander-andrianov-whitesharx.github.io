import sys
import ssl
from http.server import HTTPServer, SimpleHTTPRequestHandler


class GzipRequestHandler(SimpleHTTPRequestHandler):
    '''HTTPRequestHandler for gzip files'''

    def end_headers(self):
        '''Set Content-Encoding: gzip for gzipped files'''
        if hasattr(self, 'path') and self.path.endswith('.gz'):
            self.send_header('Content-Encoding', 'gzip')
        super().end_headers()

    def do_GET(self):
        '''Set Content-Encoding and Content-Type to gzipped files'''
        path = self.translate_path(self.path)
        if path.endswith('.js.gz'):
            try:
                with open(path, 'rb') as f:
                    content = f.read()
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/javascript')
                    self.end_headers()
                    self.wfile.write(content)
            except FileNotFoundError:
                self.send_error(404, 'File Not Found')
        elif path.endswith('.wasm.gz'):
            try:
                with open(path, 'rb') as f:
                    content = f.read()
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/wasm')
                    self.end_headers()
                    self.wfile.write(content)
            except FileNotFoundError:
                self.send_error(404, 'File Not Found')
        elif path.endswith('.gz'):
            try:
                with open(path, 'rb') as f:
                    content = f.read()
                    self.send_response(200)
                    self.send_header('Content-Type', self.guess_type(path))
                    self.end_headers()
                    self.wfile.write(content)
            except FileNotFoundError:
                self.send_error(404, 'File Not Found')
        else:
            super().do_GET()


def serve(ip: str, port: int, certfile: str, keyfile: str):
    '''Run a local HTTPS server'''
    httpd = HTTPServer((ip, port), GzipRequestHandler)
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile=certfile, keyfile=keyfile)
    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
    print(f"Serving at https://{ip}:{port}")
    httpd.serve_forever()


if __name__ == "__main__":
    try:
        if len(sys.argv) != 5:
            print(f'usage: {sys.argv[0]} [IP] [PORT] [CERTFILE] [KEYFILE]')
        ip = sys.argv[1]
        port = int(sys.argv[2])
        certfile = sys.argv[3]
        keyfile = sys.argv[4]
        serve(ip, port, certfile, keyfile)
    except Exception as e:
        print('Error:', e)