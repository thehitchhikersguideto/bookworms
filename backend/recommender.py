import pandas as pd

# Recommendation Method
def get_recommendations(user_books):
    # For now just return a dictionary of books with title, author, _id and image
    return [
        {
            "id": "1",
            "title": "The Hunger Games",
            "author": ["Suzanne Collins"],
            "image": "placeholder"
        },
        {
            "id": "2",
            "title": "Harry Potter and the Sorcerer's Stone",
            "author": ["J.K. Rowling"],
            "image": "placeholder"
        },
        {
            "id": "3",
            "title": "To Kill a Mockingbird",
            "author": ["Harper Lee"],
            "image": "placeholder"
        } 
        ]