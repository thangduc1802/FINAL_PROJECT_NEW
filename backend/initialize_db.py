import os
import logging
import database
import sqlite3

# Configure logging

def create_database_tables():
    try:
        # This function creates the necessary tables
        database.create_user_table()
        logging.info("Database tables were successfully created.")
    except Exception as e:
        logging.error(f"An error occurred while creating database tables: {e}")
#create_database_tables()
# Run the function to create tables
#create_database_tables()

def print_all_users():
    """
    Label: Print All Users Function

    Short Description:
    Connects to the SQLite database and prints all records from the 'users' table.

    Parameters:
    - None.

    Return:
    - None: Outputs user data to the console.
    """
    connection = sqlite3.connect('database.db')  # Replace with your database name
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    
    for user in users:
        print(user)

    connection.close()

print_all_users()
def delete_database():
    """
    Deletes the SQLite database file 'database.db'.

    Returns:
        None

    Tests:
        1. **Database Deletion Success**:
            - Input: Call `delete_database()` when 'database.db' exists.
            - Expected Outcome: The database file is deleted and an info log is created.
        
        2. **Database File Not Found**:
            - Input: Call `delete_database()` when 'database.db' does not exist.
            - Expected Outcome: A warning log is created, indicating that the file was not found.
    """
    db_path = 'database.db'

    try:
        if os.path.exists(db_path):
            os.remove(db_path)
            logging.info("Database file '%s' deleted successfully.", db_path)
        else:
            logging.warning("Database file '%s' not found for deletion.", db_path)
    except OSError as e:
        logging.error("Error deleting database file '%s': %s", db_path, e)
        raise e
#delete_database()