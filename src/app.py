from flask import Flask, render_template, request, redirect, url_for, session,flash
import os,signal
from socket_wrapper import Client 



class ClientManager:
    
    def __init__(self):
        self.app = Flask(__name__, template_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ui')))
        self.app.secret_key = "your-secret-key"
        self._setup_routes()
        ip,port = "127.0.0.1",12344

        self.client = Client(ip,port)  # Connects to your socket server
        self.client.send_by_size(self.client.client_hello())
        self.client.recv_by_size()
        
        
        
        self.app.run(debug=True,use_reloader=False)

    def _setup_routes(self):
        """Register all Flask routes with corresponding class methods."""
        self.app.route('/start_menu')(self.start_menu)
        self.app.route('/login', methods=['GET', 'POST'])(self.login)
        self.app.route('/signup', methods=['GET', 'POST'])(self.signup)
        self.app.route('/main_menu')(self.main_menu)
        self.app.route('/add_url', methods=['GET', 'POST'])(self.add_url)
        self.app.route('/remove_url', methods=['GET', 'POST'])(self.remove_url)
        self.app.route('/get_real_url', methods=['GET', 'POST'])(self.get_real_url)
        self.app.route('/req_info', methods=['GET', 'POST'])(self.req_info)
    
    def exit(self):
        """Handle application exit"""
        self.cleanup()
        os.kill(os.getpid(), signal.SIGINT)
        return '', 204

    def cleanup(self):
        print("Exiting client")
        self.client.cleanup()
    



    def start_menu(self):
        # Display the main menu where users can add/remove URLs or request info.
        return render_template('menu.html')


    def login(self):
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

            to_flash,category = self.client.parse(response)

            flash(to_flash,category)
            return redirect(url_for('login'))

        return render_template('login.html')



    def signup(self):
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
            if response == b'': # Server disconnected
                self.exit()

            to_flash,category = self.client.parse(response)

            flash(to_flash,category)
            if category.lower() == "error":
                return redirect(url_for('signup'))
            else:
                flash("Please Log In")
                return redirect(url_for("login"))

        return render_template('signup.html')


    def main_menu(self):
        return render_template('main_menu.html')


    def add_url(self):
        if request.method == 'POST':
            fake_url = request.form['url']

            # Send the add URL request
            data = self.client.add_url(fake_url)
            self.client.send_by_size(data)

            # Receive and parse the server response
            response = self.client.recv_by_size()
            if response == b'': # Server disconnected
                self.exit()

            to_flash,category = self.client.parse(response)

            flash(to_flash,category)
            return redirect(url_for('add_url'))

        return render_template('add_url.html')


    def remove_url(self):
        if request.method == 'POST':
            fake_url = request.form['url']

            # Send the remove URL request
            data = self.client.remove_url(fake_url)
            self.client.send_by_size(data)

            # Receive and parse the server response
            response = self.client.recv_by_size()
            if response == b'': # Server disconnected
                self.exit()

            to_flash,category = self.client.parse(response)

            flash(to_flash,category)
            return redirect(url_for('remove_url'))

        return render_template('remove_url.html')


    def get_real_url(self):
        if request.method == 'POST':
            fake_url = request.form['url']

            # Send the get real URL request
            data = self.client.get_real_url(fake_url)
            self.client.send_by_size(data)

            # Receive and parse the server response
            response = self.client.recv_by_size()
            parsed_response = self.client.parse(response)

            # Handle server response
            response = self.client.recv_by_size()
            if response == b'': # Server disconnected
                self.exit()

            to_flash,category = self.client.parse(response)

            flash(to_flash,category)
            return redirect(url_for('get_real_url'))

        return render_template('get_real_url.html')


    def req_info(self):
        if request.method == 'POST':
            fake_url = request.form['url']

            # Send the request info request
            data = self.client.req_info(fake_url)
            self.client.send_by_size(data)

            # Receive and parse the server response
            response = self.client.recv_by_size()
            if response == b'': # Server disconnected
                self.exit()

            to_flash,category = self.client.parse(response)

            flash(to_flash,category)
            return redirect(url_for('req_info'))

        return render_template('req_info.html')


if __name__ == '__main__':
    ClientManager()