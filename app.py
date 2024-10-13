"""
Book Recommendation App

- This Flask application serves as a front-end for a book recommendation system. 
- Users can register, log in, search for books using the Google Books API, and save their favorites. 
- Favorites are stored in JSON format, and users can manage them through the app.

Author: Paul, Tim, Thang
Date: 06.10.2024
Version: 0.1.0 (major.minor.bugfix)
License: Free
"""

from flask import Flask, render_template, request, redirect, session, url_for
from backend import database, google_books_api, json_storage
import logging
import sqlite3



app = Flask(__name__)
"""We used one static hardcoded key, for developing reasons"""
app.secret_key = ('VJ8_zl5jBLD2Rh0KM9M8xv1S7Jh7-UzXGvHb0ljhA1x7x3u4a6mA')


logging.basicConfig(
filename='application.log', 
level=logging.INFO, 
format='%(asctime)s - %(levelname)s - %(message)s')



@app.route('/')
def index():
    """
    Label: Index Function

    Short Description:
    Displays the homepage with streak information if the user is logged in.
    Redirects to the registration page if no user is logged in.

    Parameters:
    - None.

    Return:
    - Redirect or RenderedTemplate: Redirects to registration if no user is logged in.
      Otherwise, it renders the homepage (`index.html`) with optional streak data.

    Tests:
    - Test 1: User Logged In
      - Input: User ID is present in the session.
      - Expected Outcome: Retrieves the user's streak data and renders the homepage with this information.
    
    - Test 2: User Not Logged In
      - Input: No user ID present in the session.
      - Expected Outcome: Redirects the user to the registration page.
    """
    user_id = session.get('user_id')

    # Check if the user is logged in
    if not user_id:
        logging.info("Unauthenticated access attempt to the homepage. Redirecting to registration.")
        return redirect('/register')

    # If the user is logged in, retrieve their streak data
    streak_data = database.get_user_streak_data(user_id)
    if streak_data:
        logging.info("Displayed streak data for user ID: %s with current streak: %d days, longest streak: %d days.",
                     user_id, streak_data.get('current_streak', 0), streak_data.get('longest_streak', 0))
    else:
        logging.info("User ID %s is logged in, but no streak data found.", user_id)

    return render_template('index.html', streak_data=streak_data)


@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Label: Register Function

    Short Description:
    Handles user registration by displaying the registration form and processing user input to create a new account.

    Parameters:
    - None.

    Return:
    - RenderedTemplate: Displays the registration form (`register.html`) if the request method is GET or if registration fails.
    - Redirect: Redirects to the login page (`/login`) if registration is successful (POST request).

    Tests:
    
    - Test 1: Successful Registration
      - Input: Call `register()` with a POST request containing a valid username and password.
      - Expected Outcome: The function registers the user, saves their credentials, and redirects to the `/login` page.
    
    - Test 2: Duplicate Registration
      - Input: Call `register()` with a POST request using a username that already exists.
      - Expected Outcome: The function displays an error message in the `register.html` template.
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Attempt to register the user and check the result
        registration_success = database.register_user(username, password)
        if registration_success:
            logging.info("User '%s' registered successfully.", username)
            return redirect('/login')
        else:
            # Show an error message if registration failed due to a duplicate username
            return render_template('register.html', error="Username already exists. Please choose another one.")
    
    logging.info("Registration form accessed.")
    return render_template('register.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Label: Login Function

    Short Description:
    Handles user login by displaying the login form and authenticating user credentials.

    Parameters:
    - None.

    Return:
    - RenderedTemplate: Displays the login form (`login.html`) if the request method is GET.
    - Redirect: Redirects to the homepage (`/`) if login is successful (POST request).
    - String: Returns an error message if login fails due to incorrect username or password.

    Tests:
    - Test 1: Display Login Form
      - Input: Call `login()` with a GET request.
      - Expected Outcome: The function returns the `login.html` template for the user to fill out.
    
    - Test 2: Successful Login
      - Input: Call `login()` with a POST request containing valid username and password.
      - Expected Outcome: The function authenticates the user, sets the session with the user ID, and redirects to the homepage.
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Authenticate the user
        user = database.authenticate_user(username, password)
        if user:
            session['user_id'] = user[0]  # Store user ID in session
            logging.info("User '%s' logged in successfully.", username)
            return redirect('/')
        
        logging.warning("Login attempt failed for username '%s'.", username)
        return 'Login failed. Please check your username and password.'

    logging.info("Login form accessed.")
    return render_template('login.html')



@app.route('/logout')
def logout():
    """
    Label: Logout Function

    Short Description:
    Logs out the current user by removing their session data and redirects them to the homepage.

    Parameters:
    - None.

    Return:
    - Redirect: Redirects the user to the homepage (`/`).

    Tests:
    - Test 1: User Logout
      - Input: Call `logout()` with a user currently logged in.
      - Expected Outcome: The user session is cleared, and the user is redirected to the homepage.
    
    - Test 2: Logout Without Active Session
      - Input: Call `logout()` when no user is logged in.
      - Expected Outcome: The function executes without error and redirects to the homepage.
    """
    session.pop('user_id', None)
    logging.info("User logged out.")
    return redirect('/')


@app.route('/search', methods=['GET', 'POST'])
def search():
    """
    Label: Search Function

    Short Description:
    Displays the search form and processes the user's search query to find books 
    using the Google Books API.

    Parameters:
    - None.

    Return:
    - RenderedTemplate: Displays the search results page (`results.html`) if the request method is POST 
      and the search is successful.
    - RenderedTemplate: Displays the search form (`search.html`) if the request method is GET.
    - Redirect: Redirects to the login page (`/login`) if the user is not logged in.

    Tests:
    - Test 1: Display Search Form
      - Input: Call `search()` with a GET request while logged in.
      - Expected Outcome: The function returns the `search.html` template for the user to enter search criteria.
    
    - Test 2: Search Books with Valid Input
      - Input: Call `search()` with a POST request containing a valid field of interest and specific topic.
      - Expected Outcome: The function retrieves books from the Google Books API, logs the search action, and 
        displays the `results.html` template with the search results.
    """
    if 'user_id' not in session:
        logging.warning("Unauthorized access to search page.")
        return redirect('/login')  # User must be logged in

    if request.method == 'POST':
        field_of_interest = request.form['field']
        specific_topic = request.form.get('topic', '')

        # Retrieve books from the Google Books API based on search criteria
        books = google_books_api.search_books(field_of_interest, specific_topic)
        logging.info(
            "Search query '%s' with topic '%s' returned %d results.",
            field_of_interest, specific_topic, len(books)
        )
        return render_template('results.html', books=books, category=field_of_interest)

    logging.info("Search form accessed.")
    return render_template('search.html')



@app.route('/favorites', methods=['GET'])
def favorites():
    """
    Label: Favorites Function

    Short Description:
    Displays the user's favorite books, optionally filtered by a selected category.

    Parameters:
    - None.

    Return:
    - RenderedTemplate: Displays the `favorites.html` template with the user's favorite books.
      If a category filter is applied, only favorites matching the category are shown.

    Tests:
    - Test 1: Display All Favorites
      - Input: Call `favorites()` with a GET request without any category filter.
      - Expected Outcome: The function displays all favorite books for the logged-in user.
    
    - Test 2: Display Favorites by Category
      - Input: Call `favorites()` with a GET request including a category filter.
      - Expected Outcome: The function filters the user's favorites by the specified category 
        and displays only the matching books.
    """
    user_id = session.get('user_id')

    # Load all favorites and filter only the current user's favorites
    all_favorites = json_storage.load_all_favorites()
    favorites_json = all_favorites.get(str(user_id), [])

    # Optional: Filter by category
    category_filter = request.args.get('category', None)
    if category_filter:
        favorites_json = [
            book for book in favorites_json if book.get('category') == category_filter
        ]

    logging.info(
        "Favorites displayed for user %s with category filter '%s'.",
        user_id, category_filter
    )
    return render_template('favorites.html', favorites=favorites_json, category_filter=category_filter)


@app.route('/remove_favorites', methods=['POST'])
def remove_favorites_view():
    """
    Label: Remove Favorites Function

    Short Description:
    Handles removing selected favorite books for a user based on provided ISBNs.

    Parameters:
    - None.

    Return:
    - Redirect: Redirects to the favorites page (`/favorites`) after successful removal.
    - Redirect: Redirects to the login page (`/login`) if the user is not logged in.

    Tests:
    - Test 1: Remove Selected Favorites
      - Input: Call `remove_favorites_view()` with a POST request and a list of selected ISBNs.
      - Expected Outcome: The function removes the books with the provided ISBNs from the user's favorites 
        and redirects to the favorites page.
    
    - Test 2: Unauthorized Removal Attempt
      - Input: Call `remove_favorites_view()` without being logged in.
      - Expected Outcome: The function logs a warning and redirects the user to the login page.
    """
    if 'user_id' in session:
        user_id = session['user_id']
        selected_isbns = request.form.getlist('selected_books')

        if selected_isbns:
            json_storage.remove_favorites(user_id, selected_isbns)
            logging.info(
                "Removed favorites for user %s: %s", user_id, selected_isbns
            )

        return redirect(url_for('favorites'))

    logging.warning("Unauthorized attempt to remove favorites.")
    return redirect(url_for('login'))

@app.route('/add_favorite', methods=['POST'])
def add_favorite():
    """
    Label: Add Favorite Function

    Short Description:
    Adds selected books to the user's favorites list based on provided details.

    Parameters:
    - None.

    Return:
    - Redirect: Redirects to the favorites page (`/favorites`) after successfully adding books.
    - Tuple: Returns a message with a status code 400 if no books are selected or data is missing.

    Tests:
    - Test 1: Add Books to Favorites
      - Input: Call `add_favorite()` with a POST request containing valid book details.
      - Expected Outcome: The function adds the selected books to the user's favorites and 
        redirects to the favorites page.
    
    - Test 2: Add Books without selecting one 
      - Input: Call `add_favorite()` with a POST request containing no selected books.
      - Expected Outcome: The function logs an error and returns "No books selected to add to favorites".
    """
    user_id = session.get('user_id')

    selected_books = request.form.getlist('selected_books')
    if not selected_books:
        logging.error("No books selected to add to favorites.")
        return "No books selected.", 400

    for index in selected_books:
        title = request.form.get(f'title_{index}')
        author = request.form.get(f'author_{index}')
        isbn = request.form.get(f'isbn_{index}')
        publication_year = request.form.get(f'publication_year_{index}')
        category = request.form.get(f'category_{index}', 'Uncategorized')

        if not all([title, author, isbn, publication_year]):
            logging.error("Missing data for one of the books.")
            return "Missing data for one of the books.", 400

        # Prepare book details
        book_details = {
            'title': title,
            'author': author,
            'isbn': isbn,
            'publication_year': publication_year,
            'category': category
        }

        json_storage.save_favorite(user_id, book_details)
        logging.info(
            "Added favorite book '%s' for user %s.",
            title, user_id
        )

    return redirect('/favorites')



@app.route('/bookmark', methods=['GET'])
def bookmark():
    """
    Label: Bookmark Function

    Short Description:
    Displays the user's bookmarked books.

    Parameters:
    - None.

    Return:
    - RenderedTemplate: Displays the `bookmarks.html` template with the user's bookmarked books.
    - Redirect: Redirects to the login page (`/login`) if the user is not logged in.

    Tests:
    - Test 1: Display Bookmarks
      - Input: Call `bookmark()` with a GET request while logged in.
      - Expected Outcome: The function retrieves and displays the user's bookmarked books on the `bookmarks.html` page.
    
    - Test 2: Unauthorized Access to Bookmarks
      - Input: Call `bookmark()` with a GET request without being logged in.
      - Expected Outcome: The function logs a warning and redirects the user to the login page.
    """
    user_id = session.get('user_id')
    if not user_id:
        logging.warning("Unauthorized access to bookmarks.")
        return redirect('/login')

    # Load all favorites and filter for the current user
    all_favorites = json_storage.load_all_favorites()
    favorites = all_favorites.get(str(user_id), [])

    logging.info("Displayed bookmarks for user %s.", user_id)
    return render_template('bookmarks.html', favorites=favorites)


# Configure logging to write to a file
logging.basicConfig(
    filename='app.log',  # Name of the log file
    level=logging.INFO,  # Log level (use DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(levelname)s - %(message)s'
)

@app.route('/update_current_page', methods=['POST'])
def update_current_page():
    """
    Label: Update Favorite Page Function

    Short Description:
    Updates the current page for a user's favorite book and updates the user's reading streak.

    Parameters:
    - None.

    Return:
    - RenderedTemplate: Renders the `bookmarks.html` template with the updated favorites list.
    - Redirect: Redirects to the login page (`/login`) if the user is not logged in.
    - Tuple: Returns a message with a 400 status code if the provided page number is invalid.

    Tests:
    - Test 1: Update Favorite Page with Valid Data
      - Input: Call `update_current_page()` with a valid book ISBN and page number.
      - Expected Outcome: The function updates the book's current page, updates the reading streak, 
        and displays the updated bookmarks.
    
    - Test 2: Unauthorized Access
      - Input: Call `update_current_page()` an user is not logged in.
      - Expected Outcome: The function redirects the user to the login page (`/login`)
    """
    user_id = session.get('user_id')
    if not user_id:
        logging.warning("Unauthorized attempt to update favorite page.")
        return redirect('/login')  # User must be logged in

    # Get data from the form
    book_isbn = request.form['book_isbn']
    current_page = request.form['current_page']

    try:
        current_page = int(current_page)  # Ensure page number is a valid integer
    except ValueError:
        logging.error("Invalid page number '%s' provided.", current_page)
        return "Invalid page number", 400

    # Update the current page in the JSON file
    json_storage.update_current_page(user_id, book_isbn, current_page)
    logging.info(
        "Updated page to %d for book with ISBN %s for user %s.",
        current_page, book_isbn, user_id
    )

    # Update the user's reading streak
    database.update_reading_streak(user_id)

    # Reload the page with the updated data
    favorites = json_storage.load_user_favorites(user_id)
    return render_template('bookmarks.html', favorites=favorites)



@app.route('/learnings', methods=['GET', 'POST'])
def learnings():
    """
    Label: Learnings Function

    Short Description:
    Displays and saves learning notes for a user's favorite books.

    Parameters:
    - None.

    Return:
    - RenderedTemplate: Renders the `learnings.html` template with the user's favorites and saved notes.
    - Redirect: Redirects to the login page (`/login`) if the user is not logged in.
    - Redirect: Redirects back to the learnings page after saving notes.

    Tests:
    - Test 1: Display Learnings
      - Input: Call `learnings()` with a GET request while logged in.
      - Expected Outcome: The function retrieves and displays the user's favorite books and any saved learning notes.
    
    - Test 2: Save Learning Note
      - Input: Call `learnings()` with a POST request containing a book ISBN and a learning note.
      - Expected Outcome: The function saves the note for the specified book, logs the action, 
        and redirects to the `learnings` page.
    """
    user_id = session.get('user_id')
    if not user_id:
        logging.warning("Unauthorized access to learnings.")
        return redirect('/login')

    if request.method == 'POST':
        book_isbn = request.form['book_isbn']
        learning = request.form['learning']

        json_storage.save_learning(user_id, book_isbn, learning)
        logging.info(
            "Saved learning for book with ISBN %s for user %s.",
            book_isbn, user_id
        )

        return redirect('/learnings')

    favorites = json_storage.load_user_favorites(user_id)
    return render_template('learnings.html', favorites=favorites)




if __name__ == '__main__':
    app.run(debug=True)
