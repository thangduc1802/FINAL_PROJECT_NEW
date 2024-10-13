"""
Google Books API Module

- This module interacts with the Google Books API to search for books based on user input and retrieve book details using the ISBN.

Author: Paul, Tim, Thang
Date: 06.10.2024
Version: 0.1.0
License: Free
"""

import requests
import logging

# Set up logging configuration
logging.basicConfig(filename='application.log', 
                    level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def search_books(field_of_interest, specific_topic):
    """
    Searches for books based on the field of interest and specific topic using the Google Books API.

    Args:
        field_of_interest (str): The general category or subject area of interest.
        specific_topic (str): An optional specific topic or subcategory within the field of interest.

    Returns:
        list: A list of dictionaries containing details for up to 10 books. 
              Each dictionary contains the following book details:
              - 'title': Title of the book (str).
              - 'author': Author(s) of the book (str).
              - 'isbn': The ISBN of the book (str).
              - 'publication_year': Year of publication (str).
              - 'description': Description of the book (str).
              - 'category': The category or field of interest (str).

    Tests:
        1. Valid Search Query:
            - Input: `field_of_interest = "Science"`, `specific_topic = "Physics"`
            - Expected Outcome: The function should return a list of up to 10 dictionaries, each containing book details like 'title', 'author', 'isbn', etc. All fields should be populated with relevant data.

        2. Empty Specific Topic:
            - Input: `field_of_interest = "Wirtschaft"`, `specific_topic = ""`
            - Expected Outcome: The function should return a list of up to 10 dictionaries containing fiction books without any filtering by specific topic. The books should still have their details populated correctly.
        
    """
    query = f'{field_of_interest} {specific_topic}'
    url = f'https://www.googleapis.com/books/v1/volumes?q={query}'
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        logging.info(f"Search query for '{query}' returned {len(data.get('items', []))} results.")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching books from Google Books API for query '{query}': {e}")
        return []

    books = []
    for item in data.get('items', [])[:10]:  # Limit to 10 books
        book_info = item.get('volumeInfo', {})

        # Add book details
        books.append({
            'title': book_info.get('title', 'N/A'),
            'author': ', '.join(book_info.get('authors', ['N/A'])),
            'isbn': book_info.get('industryIdentifiers', [{'identifier': 'N/A'}])[0]['identifier'],
            'publication_year': book_info.get('publishedDate', 'N/A'),
            'description': book_info.get('description', 'No description available'),
            'category': field_of_interest  # Add the field of interest as the category
        })

    logging.info(f"Successfully retrieved {len(books)} books for query '{query}'.")
    return books


