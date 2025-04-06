import json,threading,os,re

import smtplib,ssl,random
from functools import wraps
from email.message import EmailMessage



class Users:
    lock = threading.Lock()
    
    @staticmethod
    def manage_users(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with Users.lock:
                users = load_users()
            
            result = func(users, *args, **kwargs)
            
            with Users.lock:
                json.dump(users, open('users.json', 'w'))

            return result
        
        return wrapper
    
    
    
    @staticmethod
    @manage_users
    def does_user_exists(users,user: str) -> bool:
        return user in users.keys()
    
    @staticmethod
    @manage_users
    def check_sign_in(users,username, password) -> bytes:
        with Users.lock:
            if not Users.does_user_exists(username): #type:ignore
                to_send = b"ERR~4~Username not found"
            elif not users[username][0] == password:
                to_send = b"ERR~4~wrong password"
            
            else:
                to_send = b"ACK"
        return to_send

    @staticmethod
    @manage_users
    def get_salt(users,username : str) -> str:
        try:
            return users[username][1]
        except:
            return "" #if user doesn't exist it doesn't matter what we return, when trying to log in it will fail anyway
    
    @staticmethod
    @manage_users
    def sign_up(users,username: str, password :str, cpassword: str,salt: str) -> bytes:
        
        #check for errors
        if Users.does_user_exists(username): #type:ignore
            to_send = b"ERR~3~username already exists"
        elif password != cpassword:
            to_send = b"ERR~3~passwords aren't identical"
        elif not is_valid(username):
            to_send = b"ERR~3~Please enter a valid email!"
        
        #actually sign up
        else:
            users[username] = password,salt
            to_send = b"ACK"
        
        
        return to_send

    @staticmethod
    def create_salt() -> str:
        return os.urandom(4).hex()


    def clear(self):
        os.remove("users.json")
    




def load_users() -> dict:
    try:
        with open('users.json', 'r') as file:
            return json.load(file)
    except:
        return {}


def is_valid(email) -> bool:
    return re.match(r"^[A-Za-z_0-9\.]+@[A-Za-z_0-9\.]+\.[A-Za-z_0-9]+",email) is not None