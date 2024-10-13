## Who we are
Tim Rösch, 
Thang, 
Paul Willy


### How to start the application.

1. Requirements installieren pip install -r requirements.txt

2. Initialize Database with =>  python initialize_db.py

3. Run the flaks application with => python app.py 

4. Open this link http://127.0.0.1:5000 in your browser

5. Have fun with the application.


## What we want to show.

### The Application
The Book Management App is a web-based application designed to support self-learning by providing users with an intuitive platform for discovering, tracking, and managing books that align with the users interests. It follows a client-server architecture, where the frontend interacts with the backend through a set of API endpoints. This interaction enables users to perform actions like searching for books, saving their favorites, tracking their reading progress, and recording key learnings from each book. By integrating a feature like reading streaks, the app motivates continuous learning and self-improvement. The backend manages user data and book information. Its like a libary, the whole book is not intergrated so the user can not buy or read books with the application. The frontend dynamically updates based on user interactions, ensuring a responsive and engaging experience tailored to the user's self-learning journey.

### Frontend:
We developed the Frontend with HTML, CSS and Java Script to create a responsive user interface.
We utilized Jinja2 templates to render pages based on the data from the backend.
CSS is used for styling and ensuring the application has a clean and modern design.
JavaScript enables interactivity, such as handling form submissions and toggling UI elements.

Our idea was to be creative in this project, therefor we created several different pages, with differnet operations.

### Backend:

We used the python-based web frameork Flask, to manage our API endpoints, process user input and serve responses.
Additionally we intergated the Google Books API in our Application as a external data source for books.

#### We had to implement two different storages, 

1. We used SQLite to create a database for the user information
2. We used a JSON file to store user specific data, like learnings, bookmarks and his favorite books.



### Communication between Frontend and Backend

In our Book Management App, communication between the frontend and backend occurs through HTTP requests. The frontend, built with HTML, CSS, and JavaScript, sends GET and POST requests to Flask-based API endpoints on the backend. When a user interacts with the application, such as logging in, searching for books, or updating their reading progress, the frontend sends a POST request containing the user input to the appropriate backend route. Flask processes these requests by interacting with the SQLite database (for user data) or external services like the Google Books API (for book search). The backend processes the data and sends a response back to the frontend, which dynamically updates the interface using templates rendered with Jinja2. This architecture ensures seamless data flow between the user interface and the server, allowing the app to provide personalized, real-time experiences.

### Special Operations 

- Personalized Book Search: Uses Google Books API for tailored recommendations, helping users find books that align with their learning interests.

- Reading Progress Tracking: Users can track their progress, set bookmarks and build up streaks

- Learning Notes: Allows users to save important insights and reflections on their readings, supporting deeper understanding.

- Favorites Management: Users can save favorite books, creating a personalized library to revisit and study. The favorites are are stored in a JSON file.

- Secure Data Handling: Uses SQLite for storing hashed/crypted user data and learning progress.

### Note 
- We documented the html code and the css code as well. 
- The documentaion and general tests for html are above the code in every html template. => folder templates
- The documentation and general tests for css are intergated in the css code => folder static

## additional readme informations
- autodoc from code docstrings -> mkdocs






