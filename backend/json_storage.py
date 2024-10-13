"""
Favorites Management Module

- This module provides functionality to manage users' favorite books using a JSON file for storage. 
- Users can save their favorite books, add notes about their learning, update the current page they are on, and remove books from their favorites list.

Author: Paul, Tim, Thang
Date: 06.10.2024
Version: 0.1.0
License: Free
"""

import json
import os
import logging

# Path to the JSON file for favorites
FAVORITES_JSON_PATH = 'favorites.json'

# Set up logging configuration
logging.basicConfig(filename='application.log', 
                    level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')


def load_all_favorites():
    """
    Label: Load All Favorites Function

    Short Description:
    Loads all favorite books for each user from a JSON file.

    Parameters:
    - None.

    Return:
    - dict: A dictionary where keys are user IDs and values are lists of favorite books for each user.
            Returns an empty dictionary if the file doesn't exist or is not readable.

    Tests:
    - Test 1: File Exists
      - Input: A valid JSON file located at `FAVORITES_JSON_PATH`.
      - Expected Outcome: The function should return a dictionary containing the user's favorite books 
        as loaded from the JSON file.
    
    - Test 2: File Does Not Exist
      - Input: A scenario where the JSON file does not exist.
      - Expected Outcome: The function should return an empty dictionary and log a warning message.

    """
    if not os.path.exists(FAVORITES_JSON_PATH):
        logging.warning("%s does not exist.", FAVORITES_JSON_PATH)
        return {}

    try:
        with open(FAVORITES_JSON_PATH, 'r') as file:
            logging.info("Loaded favorites from %s.", FAVORITES_JSON_PATH)
            return json.load(file)
    except json.JSONDecodeError as e:
        logging.error("Error decoding JSON file %s: %s", FAVORITES_JSON_PATH, e)
        return {}
    except IOError as e:
        logging.error("Failed to read file %s: %s", FAVORITES_JSON_PATH, e)
        return {}


def load_user_favorites(user_id):
    """
    Label: Load User Favorites Function

    Short Description:
    Loads the favorite books for a specific user from the JSON file.

    Parameters:
    - user_id (int or str): The ID of the user whose favorites should be loaded.

    Return:
    - list: A list of favorite books for the given user. Returns an empty list if 
            the user has no favorites or does not exist in the JSON data.

    Tests:
    - Test 1: User Has Favorites
      - Input: A user ID that exists in the favorites JSON file.
      - Expected Outcome: The function should return a list of favorite books for that user.
    
    - Test 2: User Has No Favorites
      - Input: A user ID that does not exist in the favorites JSON file.
      - Expected Outcome: The function should return an empty list, and a log message should indicate zero favorites.
    
    """
    all_favorites = load_all_favorites()
    favorites = all_favorites.get(str(user_id), [])

    if not favorites:
        logging.info("User %s has no favorites.", user_id)
    else:
        logging.info("Loaded %d favorites for user %s.", len(favorites), user_id)

    return favorites


def save_favorite(user_id, book_details):
    """
    Label: Save Favorite Function

    Short Description:
    Saves a favorite book for a user in the JSON file, ensuring no duplicates are added.

    Parameters:
    - user_id (int or str): The ID of the user adding a favorite.
    - book_details (dict): A dictionary containing the details of the book 
                           (e.g., title, author, ISBN).

    Return:
    - None

    Tests:
    - Test 1: Valid Save
      - Input: A user ID that exists and valid book details.
      - Expected Outcome: The book should be added to the user's favorites in the JSON file,
        and a log message should confirm the addition.
    
    - Test 2: Duplicate Book
      - Input: A user ID that exists and book details that are already in the user's favorites.
      - Expected Outcome: The user's favorites should remain unchanged, and the duplicate book should 
        not be added. A log message should indicate that the book already exists.
    """
    all_favorites = load_all_favorites()

    # Ensure the user's favorites list exists
    if str(user_id) not in all_favorites:
        all_favorites[str(user_id)] = []

    # Check if the book already exists in the user's favorites
    existing_book = next(
        (book for book in all_favorites[str(user_id)] if book['isbn'] == book_details['isbn']),
        None
    )

    if not existing_book:
        all_favorites[str(user_id)].append(book_details)

        # Write the updated favorites back to the JSON file
        with open(FAVORITES_JSON_PATH, 'w') as file:
            json.dump(all_favorites, file, indent=4)
        logging.info(
            "Book '%s' added to favorites for user %s.",
            book_details['title'],
            user_id
        )
    else:
        logging.info(
            "Book '%s' already exists in favorites for user %s.",
            book_details['title'],
            user_id
        )



def save_learning(user_id, book_isbn, learning):
    """
    Label: Save Favorite Learning Function

    Short Description:
    Saves a learning note for a specific book in the user's favorites in the JSON file.

    Parameters:
    - user_id (int or str): The ID of the user.
    - book_isbn (str): The ISBN of the book for which the learning note is being saved.
    - learning (str): The learning note or takeaway from the book.

    Return:
    - None

    Tests:
    - Test 1: Valid Learning Note Update
      - Input: A user ID that exists, a valid ISBN, and a learning note.
      - Expected Outcome: The learning note should be updated in the user's favorite book entry in the JSON file,
        and a log message should confirm the update.
    
    - Test 2: Nonexistent Book
      - Input: A user ID that exists but a book ISBN that is not in the user's favorites.
      - Expected Outcome: The JSON file should remain unchanged since there’s no matching book, 
        and a warning message should be logged.
    """
    all_favorites = load_all_favorites()

    if str(user_id) in all_favorites:
        # Find the book by its ISBN and update its learning note
        for book in all_favorites[str(user_id)]:
            if book['isbn'] == book_isbn:
                book['learning'] = learning
                logging.info(
                    "Updated learning for book '%s' (ISBN: %s) for user %s.",
                    book['title'],
                    book_isbn,
                    user_id
                )
                break
        else:
            logging.warning(
                "Book with ISBN %s not found in favorites for user %s.",
                book_isbn,
                user_id
            )
            return

        # Write the updated favorites back to the JSON file
        with open(FAVORITES_JSON_PATH, 'w') as file:
            json.dump(all_favorites, file, indent=4)
    else:
        logging.warning(
            "User %s does not have any favorites stored.",
            user_id
        )


def remove_favorites(user_id, selected_isbns):
    """
    Label: Remove Favorites Function

    Short Description:
    Removes selected books from a user's favorites in the JSON file.

    Parameters:
    - user_id (int or str): The ID of the user.
    - selected_isbns (list): A list of ISBNs for the books to be removed from the user's favorites.

    Return:
    - None

    Tests:
    - Test 1: Valid Removal
      - Input: A user ID that exists and a list of ISBNs that are present in the user's favorites.
      - Expected Outcome: The specified books should be removed from the user's favorites in the JSON file,
        and a log message should confirm the removal.
    
    - Test 2: No Matching ISBNs
      - Input: A user ID that exists and a list of ISBNs that are not in the user's favorites.
      - Expected Outcome: The user's favorites should remain unchanged, and a log message should indicate
        that no books were removed.
    """
    all_favorites = load_all_favorites()

    if str(user_id) in all_favorites:
        initial_count = len(all_favorites[str(user_id)])
        # Filter out the books whose ISBN is in the selected_isbns list
        all_favorites[str(user_id)] = [
            book for book in all_favorites[str(user_id)] if book['isbn'] not in selected_isbns
        ]

        final_count = len(all_favorites[str(user_id)])
        removed_count = initial_count - final_count
        logging.info(
            "Removed %d books from favorites for user %s.",
            removed_count,
            user_id
        )

        # Write the updated favorites back to the JSON file
        with open(FAVORITES_JSON_PATH, 'w') as file:
            json.dump(all_favorites, file, indent=4)
    else:
        logging.warning("No favorites found for user %s.", user_id)


def update_current_page(user_id, book_isbn, current_page):
    """
    Update the current page number of a favorite book for the user.

    Parameters:
        user_id (int or str): The ID of the user.
        book_isbn (str): The ISBN of the book being updated.
        current_page (int): The new current page number the user is on.

    Returns:
        None


    Tests:
        1. **Valid Page Update**:
            - Input: A user ID that exists, a valid ISBN of a favorite book, and a new current page number.
            - Expected Outcome: The current page number for the specified book should be updated in the user's favorites in the JSON file.
        
        2. **Nonexistent Book Update**:
            - Input: A user ID that exists and an ISBN that does not match any book in the user's favorites.
            - Expected Outcome: The JSON file should remain unchanged since there’s no matching book to update.

    """
    all_favorites = load_all_favorites()

    if str(user_id) in all_favorites:
        for book in all_favorites[str(user_id)]:
            if book['isbn'] == book_isbn:
                book['current_page'] = current_page
                logging.info(
                    f"Updated current page to {current_page} for book {book['title']} "
                    f"(ISBN: {book_isbn}) for user {user_id}."
                )
                break
        else:
            logging.warning(
                f"Book with ISBN {book_isbn} not found in favorites for user {user_id}."
            )

        try:
            # Write the updated favorites back to the JSON file
            with open(FAVORITES_JSON_PATH, 'w') as file:
                json.dump(all_favorites, file, indent=4)
        except IOError as e:
            logging.error(
                f"Failed to update page for book {book_isbn} for user {user_id}: {e}"
            )
    else:
        logging.warning(f"User {user_id} not found in favorites.")
