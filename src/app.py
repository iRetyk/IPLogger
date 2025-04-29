from flask import Flask, render_template, request, redirect, url_for, session,flash
import os
from socket_wrapper import Client  # your refactored Client class

app = Flask(__name__, template_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ui')))
app.secret_key = "your-secret-key"

ip,port = "127.0.0.1",12344

client = Client(ip,port)  # Connects to your socket server
client.send_by_size(client.client_hello())

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Send login request
        data = client.login(username=username, password=password)
        client.send_by_size(data)

        # Receive and parse the server response
        response = client.recv_by_size()
        parsed_response = client.parse(response)

        # Handle server response
        if parsed_response == b'':
            return redirect(url_for('main_menu'))
        else:
            flash('Invalid username or password. Please try again.', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cpassword = request.form['cpassword']

        # Ensure passwords match
        if password != cpassword:
            flash('Passwords do not match. Please try again.', 'error')
            return redirect(url_for('signup'))

        # Send signup request
        data = client.sign_up(username=username, password=password, cpassword=cpassword)
        client.send_by_size(data)

        # Receive and parse the server response
        response = client.recv_by_size()
        parsed_response = client.parse(response)

        # Handle server response
        if parsed_response == b'':
            flash('Signup successful! Please login.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Signup failed. Please try again.', 'error')
            return redirect(url_for('signup'))

    return render_template('signup.html')


@app.route('/main_menu')
def main_menu():
    # Display the main menu where users can add/remove URLs or request info.
    return render_template('menu.html')


@app.route('/add_url', methods=['GET', 'POST'])
def add_url():
    if request.method == 'POST':
        fake_url = request.form['url']

        # Send the add URL request
        data = client.add_url(fake_url)
        client.send_by_size(data)

        # Receive and parse the server response
        response = client.recv_by_size()
        parsed_response = client.parse(response)

        # Handle server response
        if parsed_response == b'':
            flash(f'URL {fake_url} added successfully.', 'success')
            return redirect(url_for('main_menu'))
        else:
            flash(f'Failed to add URL {fake_url}. Please try again.', 'error')
            return redirect(url_for('add_url'))

    return render_template('add_url.html')


@app.route('/remove_url', methods=['GET', 'POST'])
def remove_url():
    if request.method == 'POST':
        fake_url = request.form['url']

        # Send the remove URL request
        data = client.remove_url(fake_url)
        client.send_by_size(data)

        # Receive and parse the server response
        response = client.recv_by_size()
        parsed_response = client.parse(response)

        # Handle server response
        if parsed_response == b'':
            flash(f'URL {fake_url} removed successfully.', 'success')
            return redirect(url_for('main_menu'))
        else:
            flash(f'Failed to remove URL {fake_url}. Please try again.', 'error')
            return redirect(url_for('remove_url'))

    return render_template('remove_url.html')


@app.route('/get_real_url', methods=['GET', 'POST'])
def get_real_url():
    if request.method == 'POST':
        fake_url = request.form['url']

        # Send the get real URL request
        data = client.get_real_url(fake_url)
        client.send_by_size(data)

        # Receive and parse the server response
        response = client.recv_by_size()
        parsed_response = client.parse(response)

        # Handle server response
        if parsed_response == b'':
            flash(f'Real URL for {fake_url} retrieved successfully.', 'success')
            return redirect(url_for('main_menu'))
        else:
            flash(f'Failed to retrieve real URL for {fake_url}. Please try again.', 'error')
            return redirect(url_for('get_real_url'))

    return render_template('get_real_url.html')


@app.route('/req_info', methods=['GET', 'POST'])
def req_info():
    if request.method == 'POST':
        fake_url = request.form['url']

        # Send the request info request
        data = client.req_info(fake_url)
        client.send_by_size(data)

        # Receive and parse the server response
        response = client.recv_by_size()
        parsed_response = client.parse(response)

        # Handle server response
        if parsed_response == b'':
            flash(f'Information for {fake_url} retrieved successfully.', 'success')
            return redirect(url_for('main_menu'))
        else:
            flash(f'Failed to retrieve information for {fake_url}. Please try again.', 'error')
            return redirect(url_for('req_info'))

    return render_template('req_info.html')


if __name__ == '__main__':
    app.run(debug=True)