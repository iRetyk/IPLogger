import json
import threading
import os
import re
from functools import wraps
from hashlib import sha256
from typing import Dict, Tuple, Callable, TypeVar, Any, cast

T = TypeVar('T')
UserData = Tuple[str, str]  # (hashed_password, salt)
UserDict = Dict[str, UserData]

def manage_users(func: Callable[..., T]) -> Callable[..., T]:
    """
    Input: func (Callable) - Function to decorate
    Output: Callable - Wrapped function with user management
    Purpose: Manage user data file access
    Description: Decorator that handles loading and saving user data with thread safety
    """
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        with Users.lock:
            users = load_users()

        result = func(users, *args, **kwargs)

        with Users.lock:
            json.dump(users, open('users.json', 'w'))

        return result

    return wrapper

class Users:
    """Class for managing user authentication and data."""

    lock = threading.Lock()

    @staticmethod
    @manage_users
    def does_user_exists(users: UserDict, user: str) -> bool:
        """
        Input: users (UserDict) - User dictionary, user (str) - Username to check
        Output: bool - True if user exists, False otherwise
        Purpose: Check if user exists
        Description: Verifies if username exists in user database
        """
        return user in users

    @staticmethod
    @manage_users
    def check_sign_in(users: UserDict, username: str, password: str) -> bytes:
        """
        Input: users (UserDict) - User dictionary, username (str) - Username to check,
               password (str) - Password to verify
        Output: bytes - Success or error message
        Purpose: Verify user login credentials
        Description: Checks username existence and password correctness
        """
        # Check for errors
        if not Users.does_user_exists(username):  # type: ignore
            to_send = b"ERR~4~Username not found"
        elif users[username][0] != Users._hash(password + Users.get_salt(username)):  # type: ignore
            to_send = b"ERR~4~wrong password"
        else:
            to_send = b"ACK"
        return to_send

    @staticmethod
    @manage_users
    def get_salt(users: UserDict, username: str) -> str:
        """
        Input: users (UserDict) - User dictionary, username (str) - Username to get salt for
        Output: str - User's salt or empty string if user not found
        Purpose: Retrieve user's salt
        Description: Gets the salt used for password hashing for the given user
        """
        try:
            return users[username][1]
        except KeyError:
            return ""  # If user doesn't exist it doesn't matter what we return

    @staticmethod
    @manage_users
    def sign_up(users: UserDict, username: str, password: str, cpassword: str, salt: str) -> bytes:
        """
        Input: users (UserDict) - User dictionary, username (str) - Username to register,
               password (str) - Password to set, cpassword (str) - Password confirmation,
               salt (str) - Salt for password hashing
        Output: bytes - Success or error message
        Purpose: Register new user
        Description: Creates new user account with password after validation
        """
        # Check for errors
        if Users.does_user_exists(username):  # type: ignore
            to_send = b"ERR~3~username already exists"
        elif password != cpassword:
            to_send = b"ERR~3~passwords aren't identical"
        elif not is_valid(username):
            to_send = b"ERR~3~Please enter a valid email!"
        else:
            users[username] = (Users._hash(password + salt), salt)
            to_send = b"ACK"

        return to_send

    @staticmethod
    def create_salt() -> str:
        """
        Input: None
        Output: str - Generated salt string
        Purpose: Generate random salt
        Description: Creates a random hexadecimal salt for password hashing
        """
        return os.urandom(4).hex()

    @staticmethod
    def _hash(to_hash: str) -> str:
        """
        Input: to_hash (str) - String to hash
        Output: str - Hashed string
        Purpose: Create password hash
        Description: Creates SHA-256 hash of input string
        """
        return sha256(to_hash.encode()).hexdigest()

    def clear(self) -> None:
        """
        Input: None
        Output: None
        Purpose: Clear user data
        Description: Removes the users data file
        """
        os.remove("users.json")

def load_users() -> UserDict:
    """
    Input: None
    Output: UserDict - Dictionary of user data
    Purpose: Load user database
    Description: Loads user data from JSON file or returns empty dict if file not found
    """
    try:
        with open('users.json', 'r') as file:
            return json.load(file)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

def is_valid(email: str) -> bool:
    """
    Input: email (str) - Email address to validate
    Output: bool - True if valid email, False otherwise
    Purpose: Validate email format
    Description: Checks if email matches valid email format using regex
    """
    return re.match(r"^[A-Za-z_0-9\.]+@[A-Za-z_0-9\.]+\.[A-Za-z_0-9]+", email) is not None
