from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict, Optional, Tuple, Union, cast

from cli_mapper import ClientMapper

MAPPER = ClientMapper()

class RedirectHandler(BaseHTTPRequestHandler):
    """HTTP request handler for redirecting requests to specified domains."""

    def do_GET(self) -> None:
        """
        Input: None
        Output: None
        Purpose: Handle GET requests and perform redirections
        Description: Retrieves target domain for client IP and sends redirect response
        """
        # Get the website parameter, default to google if not provided
        client_ip = cast(Tuple[str, int], self.client_address)[0]
        website = MAPPER.get_domain(client_ip)


        # Add https:// if not present
        if not website.startswith('http://') and not website.startswith('https://'):
            website = 'https://' + website

        print(f"Redirecting to: {website}")

        # Send redirect response
        self.send_response(302)
        self.send_header('Location', website)
        self.end_headers()

    def do_POST(self) -> None:
        """
        Input: None
        Output: None
        Purpose: Handle POST requests
        Description: Delegates POST request handling to GET handler
        """
        # Handle POST requests the same way
        self.do_GET()

def run_http_server(port: int = 80) -> None:
    """
    Input: port (int) - Port number to listen on, defaults to 80
    Output: None
    Purpose: Start HTTP server
    Description: Creates and runs HTTP server on specified port with redirect handler
    """
    server_address = ('', port)
    httpd = HTTPServer(server_address, RedirectHandler)
    httpd.serve_forever()

if __name__ == '__main__':
    print(f"HTTP server running on port {80}...")
    run_http_server()
