import os
import signal
import jinja2
from typing import Tuple, Union
from flask import Flask, render_template, request, redirect, url_for, session, flash
from socket_wrapper import Client

class ClientManager:
    """Client manager class that handles Flask web application and socket communication."""

    def __init__(self) -> None:
        """
        Input: self (ClientManager) - instance of the ClientManager class
        Output: None
        Purpose: Initialize the Flask application and establish connection with the socket server
        Description: Sets up Flask app with templates, creates socket connection, and starts the server
        """
        self.app = Flask(__name__, template_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ui')))
        self.app.secret_key = "your-secret-key"
        self._setup_routes()
        ip, port = "127.0.0.1", 12343

        self.client = Client(ip, port)  # Connects to socket server
        self.handle_hello()

        self.app.run(debug=True, use_reloader=False)

    def handle_hello(self):
        self.client.exchange_keys()
        
    
    def _setup_routes(self) -> None:
        """
        Input: self (ClientManager) - instance of the ClientManager class
        Output: None
        Purpose: Register all Flask routes with corresponding class methods
        Description: Maps URL routes to their handling methods and sets up Jinja filters
        """
        self.app.route('/start_menu')(self.start_menu)
        self.app.route('/login', methods=['GET', 'POST'])(self.login)
        self.app.route('/', methods=['GET', 'POST'])(self.login)
        self.app.route('/signup', methods=['GET', 'POST'])(self.signup)
        self.app.route('/main_menu')(self.main_menu)
        self.app.route('/add_url', methods=['GET', 'POST'])(self.add_url)
        self.app.route('/remove_url', methods=['GET', 'POST'])(self.remove_url)
        self.app.route('/get_real_url', methods=['GET', 'POST'])(self.get_real_url)
        self.app.route('/req_info', methods=['GET', 'POST'])(self.req_info)
        
        self.app.jinja_env.filters['nl2br'] = self._nl2br_filter

    def exit(self) -> Tuple[str, int]:
        """
        Input: self (ClientManager) - instance of the ClientManager class
        Output: tuple(str, int) - empty string and status code 204
        Purpose: Handle application exit gracefully
        Description: Performs cleanup and terminates the application process
        """
        self.cleanup()
        os.kill(os.getpid(), signal.SIGINT)
        return '', 204

    def cleanup(self) -> None:
        """
        Input: self (ClientManager) - instance of the ClientManager class
        Output: None
        Purpose: Clean up resources before application exit
        Description: Performs necessary cleanup operations for the client
        """
        print("Exiting client")
        self.client.cleanup()

    def start_menu(self) -> str:
        """
        Input: self (ClientManager) - instance of the ClientManager class
        Output: str - rendered HTML template
        Purpose: Display the main menu interface
        Description: Renders the menu template where users can add/remove URLs or request info
        """
        return render_template('menu.html')

    def login(self):
        """
        Input: self (ClientManager) - instance of the ClientManager class
        Output: str - rendered HTML template or redirect response
        Purpose: Handle user login functionality
        Description: Processes login form submission, communicates with server for authentication,
                    and manages user session
        """
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']

            # Send login request
            data = self.client.login(username=username, password=password)
            self.client.send_by_size(data)

            # Receive and parse the server response
            response = self.client.recv_by_size()
            if response == b'':
                self.exit()

            to_flash, category = self.client.parse(response)

            flash(to_flash, category)
            if category.lower() == "error":
                return redirect(url_for('login'))
            else:
                return redirect(url_for("main_menu"))

        return render_template('login.html')

    def signup(self):
        """
        Input: self (ClientManager) - instance of the ClientManager class
        Output: str - rendered HTML template or redirect response
        Purpose: Handle user registration
        Description: Validates signup form data, communicates with server for registration,
                    and manages response handling
        """
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            cpassword = request.form['cpassword']

            # Ensure passwords match
            if password != cpassword:
                flash('Passwords do not match. Please try again.', 'error')
                return redirect(url_for('signup'))

            # Send signup request
            data = self.client.sign_up(username=username, password=password, cpassword=cpassword)
            self.client.send_by_size(data)

            # Receive and parse the server response
            response = self.client.recv_by_size()
            if response == b'':  # Server disconnected
                self.exit()

            to_flash, category = self.client.parse(response)

            flash(to_flash, category)
            if category.lower() == "error":
                return redirect(url_for('signup'))
            else:
                flash("Please Log In")
                return redirect(url_for("login"))

        return render_template('signup.html')

    def main_menu(self) -> str:
        """
        Input: self (ClientManager) - instance of the ClientManager class
        Output: str - rendered HTML template
        Purpose: Display the main menu after successful login
        Description: Renders the main menu template with user-specific options
        """
        return render_template('main_menu.html')

    def add_url(self):
        """
        Input: self (ClientManager) - instance of the ClientManager class
        Output: str - rendered HTML template or redirect response
        Purpose: Handle URL addition requests
        Description: Processes URL submission, communicates with server to add URL,
                    and handles response
        """
        if request.method == 'POST':
            fake_url = request.form['url']

            # Send the add URL request
            data = self.client.add_url(fake_url)
            self.client.send_by_size(data)

            # Receive and parse the server response
            response = self.client.recv_by_size()
            if response == b'':  # Server disconnected
                self.exit()

            to_flash, category = self.client.parse(response)

            flash(to_flash, category)
            return redirect(url_for('add_url'))

        return render_template('add_url.html')

    def remove_url(self):
        """
        Input: self (ClientManager) - instance of the ClientManager class
        Output: str - rendered HTML template or redirect response
        Purpose: Handle URL removal requests
        Description: Processes URL removal submission, communicates with server to remove URL,
                    and handles response
        """
        if request.method == 'POST':
            fake_url = request.form['url']

            # Send the remove URL request
            data = self.client.remove_url(fake_url)
            self.client.send_by_size(data)

            # Receive and parse the server response
            response = self.client.recv_by_size()
            if response == b'':  # Server disconnected
                self.exit()

            to_flash, category = self.client.parse(response)

            flash(to_flash, category)
            return redirect(url_for('remove_url'))

        return render_template('remove_url.html')

    def get_real_url(self):
        """
        Input: self (ClientManager) - instance of the ClientManager class
        Output: str - rendered HTML template or redirect response
        Purpose: Retrieve the real URL for a given fake URL
        Description: Communicates with server to get the original URL corresponding to
                    a shortened/fake URL
        """
        if request.method == 'POST':
            fake_url = request.form['url']

            # Send the get real URL request
            data = self.client.get_real_url(fake_url)
            self.client.send_by_size(data)

            # Receive and parse the server response
            response = self.client.recv_by_size()
            if response == b'':  # Server disconnected
                self.exit()

            to_flash, category = self.client.parse(response)

            flash(to_flash, category)
            return redirect(url_for('get_real_url'))

        return render_template('get_real_url.html')

    def req_info(self):
        """
        Input: self (ClientManager) - instance of the ClientManager class
        Output: str - rendered HTML template or redirect response
        Purpose: Request information about a specific URL
        Description: Communicates with server to get information about a specific URL entry
        """
        if request.method == 'POST':
            fake_url = request.form['url']

            # Send the request info request
            data = self.client.req_info(fake_url)
            self.client.send_by_size(data)

            # Receive and parse the server response
            response = self.client.recv_by_size()
            if response == b'':  # Server disconnected
                self.exit()

            to_flash, category = self.client.parse(response)

            flash(to_flash, category)
            return redirect(url_for('req_info'))

        return render_template('req_info.html')

    @staticmethod
    def _nl2br_filter(text: str) -> str:
        """
        Input: text (str) - text to process
        Output: str - processed text with newlines converted to HTML breaks
        Purpose: Convert newlines to HTML break tags
        Description: Jinja2 filter that replaces newline characters with HTML <br> tags
        """
        if text:
            return jinja2.utils.markupsafe.Markup(text.replace('\n', '<br>'))  # type: ignore
        return ""

if __name__ == '__main__':
    ClientManager()
