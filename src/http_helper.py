from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from cli_mapper import ClientMapper


MAPPER = ClientMapper()
class RedirectHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):

        # Get the website parameter, default to google if not provided
        website = MAPPER.get_domain(self.client_address[0])
        parsed_path = urlparse(self.path)
        params = parse_qs(parsed_path.query)
        
        
        # Add https:// if not present
        if not website.startswith('http://') and not website.startswith('https://'):
            website = 'https://' + website

        print(f"Redirecting to: {website}")

        # Send redirect response
        self.send_response(302)
        self.send_header('Location', website)
        self.end_headers()

    def do_POST(self):
        # Handle POST requests the same way
        self.do_GET()

def run_http_server(port=80):
    server_address = ('', port)
    httpd = HTTPServer(server_address, RedirectHandler)
    
    httpd.serve_forever()

if __name__ == '__main__':
    print(f"HTTP server running on port {80}...")
    run_http_server()
