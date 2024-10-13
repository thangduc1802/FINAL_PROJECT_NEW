"""
Database Module

- This module handles the SQLite database connection and operations such as user registration, authentication, and table creation for a book recommendation application.

Author: Paul, Tim, Thang
Date: 06.10.2024
Version: 0.1.0
License: Free
"""

import sqlite3
import logging
import bcrypt
import hashlib
from datetime import datetime, timedelta

# Set up logging configuration
logging.basicConfig(
    filename='application.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def connect_to_db():
    """
    Label: Connect to Database Function

    Short Description:
    Establishes a connection to the SQLite database 'database.db'.

    Parameters:
    - None.

    Return:
    - Connection: SQLite connection object to 'database.db'.


    Tests:
    - Test 1: Successful Database Connection
      - Input: Call `connect_to_db()` when the SQLite database file is available.
      - Expected Outcome: The function returns a connection object, and an info log is created for the successful connection.
    
    - Test 2: Failed Database Connection
      - Input: Call `connect_to_db()` with an invalid database path or when the database file is inaccessible.
      - Expected Outcome: The function logs an error message and raises an `sqlite3.Error`.
    """
    try:
        conn = sqlite3.connect('database.db')
        logging.info("Database connection established successfully.")
        return conn
    except sqlite3.Error as e:
        logging.error("Database connection failed: %s", e)
        raise e


def create_user_table():
    """
    Label: Create User Table Function

    Short Description:
    Creates the 'users' table in the SQLite database if it does not already exist, 
    with a UNIQUE constraint on the 'username' column.

    Parameters:
    - None.

    Return:
    - None

    Tests:
    - Test 1: Table Creation Success
      - Input: Call `create_user_table()` when the database is empty.
      - Expected Outcome: The 'users' table is created successfully without raising any errors, 
        and a log message confirms the creation.
    
    - Test 2: Table Already Exists
      - Input: Call `create_user_table()` when the 'users' table already exists.
      - Expected Outcome: The function completes without raising errors, and the existing table 
        is not affected.
    """
    conn = connect_to_db()
    cur = conn.cursor()
    try:
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                last_read_date DATE,
                current_streak INTEGER DEFAULT 0,
                longest_streak INTEGER DEFAULT 0
            )
        ''')
        logging.info("Table 'users' created or already exists with UNIQUE constraint on 'username'.")
        conn.commit()
    except sqlite3.Error as e:
        logging.error("Error creating 'users' table: %s", e)
        raise e
    finally:
        conn.close()


def register_user(username, password):
    """
    Registers a new user by storing the hashed username and password in the database.

    Args:
        username (str): The user's username.
        password (str): The user's password.

    Return:
        bool: True if registration is successful, False if a duplicate username exists.

    Tests:
        1. **Successful Registration**:
            - Input: Valid username and password.
            - Expected Outcome: User is added to the database, and no errors occur.
        
        2. **Duplicate Registration Handling**:
            - Input: Register a user with a username that already exists.
            - Expected Outcome: An appropriate error message is logged, and no duplicate entries are created.
    """
    hashed_username = hash_username(username)
    hashed_password = hash_password(password)
    conn = connect_to_db()
    cur = conn.cursor()

    try:
        # Check if the user already exists
        cur.execute("SELECT * FROM users WHERE username = ?", (hashed_username,))
        existing_user = cur.fetchone()
        if existing_user:
            logging.warning("Attempted to register a duplicate user '%s'.", username)
            return False

        # Insert the new user if no duplicate is found
        cur.execute('''
            INSERT INTO users (username, password) 
            VALUES (?, ?)
        ''', (hashed_username, hashed_password))
        conn.commit()
        logging.info("User '%s' registered successfully.", username)
        return True
    except sqlite3.Error as e:
        logging.error("Error registering user '%s': %s", username, e)
        raise e
    finally:
        conn.close()


def authenticate_user(username, password):
    """
    Label: Authenticate User Function

    Short Description:
    Authenticates the user by checking the hashed username and password against stored values in the database.

    Parameters:
    - username (str): The user's username.
    - password (str): The user's password.

    Return:
    - tuple or None: Returns the user tuple (id, username, password) if authentication is successful, otherwise None.

    Tests:
    - Test 1: Successful Authentication
      - Input: Correct username and password.
      - Expected Outcome: Returns user information if credentials match and logs an info message.
    
    - Test 2: Failed Authentication
      - Input: Incorrect username or password.
      - Expected Outcome: Returns None and logs a warning message about the failed authentication attempt.
    """
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute("SELECT id, username, password FROM users")
        users = cur.fetchall()
    except sqlite3.Error as e:
        logging.error("Error during authentication: %s", e)
        return None
    finally:
        conn.close()

    for user in users:
        stored_username_hash = user[1]
        if check_username_hash(stored_username_hash, username):
            if check_password(user[2], password):
                logging.info("User '%s' successfully authenticated.", username)
                return user

    logging.warning("Authentication failed for user '%s'.", username)
    return None


def hash_password(password):
    """
    Label: Hash Password Function

    Short Description:
    Hashes a given password using bcrypt to ensure secure storage.

    Parameters:
    - password (str): The password to be hashed.

    Return:
    - str: The hashed password as a string.

    Tests:
    - Test 1: Hash Generation
      - Input: A sample password.
      - Expected Outcome: Returns a bcrypt hash string that is different from the input password.

    - Test 2: Consistent Output
      - Input: Two identical passwords.
      - Expected Outcome: Generates different hashes due to unique salts, ensuring that the hashes are not the same even for identical passwords.
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def check_password(hashed_password, password):
    """
    Label: Check Password Function

    Short Description:
    Verifies a plain text password against its hashed version using bcrypt.

    Parameters:
    - hashed_password (str): The hashed password retrieved from the database.
    - password (str): The plain text password to verify.

    Return:
    - bool: True if the password matches the hashed version, False otherwise.

    Tests:
    - Test 1: Correct Password Verification
      - Input: A valid password and its corresponding hashed version.
      - Expected Outcome: Returns True, indicating that the password matches the hash.
    
    - Test 2: Incorrect Password Verification
      - Input: An invalid password and a stored hashed version.
      - Expected Outcome: Returns False, indicating that the password does not match the hash.
    """
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))



def hash_username(username):
    """
    Label: Hash Username Function

    Short Description:
    Hashes a given username using the SHA-256 algorithm for secure storage.

    Parameters:
    - username (str): The username to be hashed.

    Return:
    - str: The SHA-256 hash of the username as a hexadecimal string.

    Tests:
    - Test 1: Hash Generation
      - Input: A sample username.
      - Expected Outcome: Returns a SHA-256 hash string that is different from the input username.
    
    - Test 2: Consistent Hash for Same Input
      - Input: Call `hash_username()` twice with the same username.
      - Expected Outcome: Both calls should return the same hash string, verifying that the function produces consistent results.
    """

    return hashlib.sha256(username.encode('utf-8')).hexdigest()



def check_username_hash(stored_hash, username):
    """
    Label: Check Username Hash Function

    Short Description:
    Verifies if the SHA-256 hash of a provided username matches the stored hash.

    Parameters:
    - stored_hash (str): The stored hash value from the database.
    - username (str): The plain text username to verify.

    Return:
    - bool: True if the hash of the username matches the stored hash, False otherwise.

    Tests:
    - Test 1: Correct Hash Match
      - Input: A stored hash and its corresponding plain text username.
      - Expected Outcome: Returns True, indicating that the hash matches the stored value.
    
    - Test 2: Incorrect Hash Match
      - Input: A stored hash and a different plain text username.
      - Expected Outcome: Returns False, indicating that the hash does not match the stored value.
    """
    return stored_hash == hash_username(username)


def update_reading_streak(user_id):
    """
    Label: Update Reading Streak Function

    Short Description:
    Updates the user's reading streak based on their last reading date. 
    Adjusts the current streak, longest streak, and updates the last read date in the database.

    Parameters:
    - user_id (int): The ID of the user.

    Return:
    - dict: A dictionary containing the user's updated 'current_streak', 'longest_streak', 
      'last_read_date', and 'streak_status'. If an error occurs, returns default values 
      with 'streak_status' set to 'error'.

    Tests:
    - Test 1: Streak Continuation
      - Input: A user who read yesterday.
      - Expected Outcome: The 'current_streak' is incremented by 1, and 'streak_status' is 'continued'.
    
    - Test 2: Streak Reset
      - Input: A user who has not read for several days.
      - Expected Outcome: The 'current_streak' is reset to 1, and 'streak_status' is 'reset'.
    
    """
    conn = connect_to_db()
    cur = conn.cursor()

    try:
        cur.execute(
            "SELECT last_read_date, current_streak, longest_streak FROM users WHERE id = ?",
            (user_id,)
        )
        user_data = cur.fetchone()

        last_read_date_str, current_streak, longest_streak = user_data if user_data else (None, 0, 0)
        last_read_date = datetime.strptime(last_read_date_str, '%Y-%m-%d').date() if last_read_date_str else None

        today = datetime.now().date()

        if last_read_date == today:
            streak_status = "unchanged"
        elif last_read_date == today - timedelta(days=1):
            current_streak += 1
            streak_status = "continued"
        else:
            current_streak = 1
            streak_status = "reset"

        if current_streak > longest_streak:
            longest_streak = current_streak

        cur.execute(
            "UPDATE users SET last_read_date = ?, current_streak = ?, longest_streak = ? WHERE id = ?",
            (today.strftime('%Y-%m-%d'), current_streak, longest_streak, user_id)
        )
        conn.commit()

        logging.info(
            "User %s streak updated: Current streak is %d, Longest streak is %d, Status: %s.",
            user_id, current_streak, longest_streak, streak_status
        )
        return {
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "last_read_date": today,
            "streak_status": streak_status
        }

    except sqlite3.Error as e:
        logging.error("Database error while updating reading streak for user %s: %s", user_id, e)
        return {
            "current_streak": 0,
            "longest_streak": 0,
            "last_read_date": None,
            "streak_status": "error"
        }
    finally:
        conn.close()

def get_user_streak_data(user_id):
    """
    Label: Get User Streak Data Function

    Short Description:
    Retrieves the user's streak data from the database, including the current streak, 
    longest streak, and the last read date.

    Parameters:
    - user_id (int): The ID of the user.

    Return:
    - dict: A dictionary containing 'current_streak', 'longest_streak', and 'last_read_date'.
            If no data is found or an error occurs, returns default values.

    Tests:
    - Test 1: Retrieve Existing Streak Data
      - Input: A valid user ID with existing streak data.
      - Expected Outcome: Returns a dictionary with the user's actual 'current_streak', 
        'longest_streak', and 'last_read_date'.
    
    - Test 2: No Streak Data Found
      - Input: A user ID that does not exist in the database.
      - Expected Outcome: Returns a dictionary with 'current_streak' set to 0, 
        'longest_streak' set to 0, and 'last_read_date' as None.
    
    """
    conn = connect_to_db()
    cur = conn.cursor()
    
    try:
        cur.execute(
            "SELECT current_streak, longest_streak, last_read_date FROM users WHERE id = ?",
            (user_id,)
        )
        result = cur.fetchone()
        
        if result:
            current_streak, longest_streak, last_read_date = result
            return {
                "current_streak": current_streak,
                "longest_streak": longest_streak,
                "last_read_date": last_read_date
            }
        
        # No data found for the user
        return {
            "current_streak": 0,
            "longest_streak": 0,
            "last_read_date": None
        }
    except sqlite3.Error as e:
        logging.error("Error retrieving streak data for user %s: %s", user_id, e)
        return {
            "current_streak": 0,
            "longest_streak": 0,
            "last_read_date": None
        }
    finally:
        conn.close()
