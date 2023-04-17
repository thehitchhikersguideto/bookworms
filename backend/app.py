# Import required libraries and modules
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import recommender

app = Flask(__name__)
CORS(app)  # Enable CORS

# Connect to the MongoDB instance
client = MongoClient("mongodb+srv://botly:BjzvLQxlBIxWDmfm@recosystems.hyjorhd.mongodb.net/?retryWrites=true&w=majority")

db = client['Goodreads']
books_collection = db['Books']

# Endpoint for searching books in the database
@app.route('/api/search', methods=['GET'])
def search_books():
    query = request.args.get('query')

    results = books_collection.find(
        {"$or": [
            {"title": {"$regex": query, "$options": "i"}},
            {"author": {"$regex": query, "$options": "i"}}
        ]},
        {"book_id": 1, "title": 1, "author": 1}
    )

    # Format the results as expected by the frontend
    formatted_results = [
        {
            "id": str(book["book_id"]),
            "title": book["title"],
            "author": book["author"]
        }
        for book in results
    ]

    print(formatted_results)

    return jsonify(formatted_results)

@app.route('/api/recommend', methods=['POST'])
def recommend_books():
    try:
        user_books = request.json['books']
        number_of_recommendations = request.json['num_books']
        # User_books is a list of dictionaries, translate this into two lists based on the contents of the dictionaries
        user_books_ids = [book['id'] for book in user_books]
        user_ratings = [book['rating'] for book in user_books]
        recommendations = recommender.get_recommendations(user_books_ids=user_books_ids, user_ratings=user_ratings, books_to_return=number_of_recommendations)
        return jsonify(recommendations)
    except KeyError:
        # Return a 400 Bad Request response if the 'books' key is missing from the request body
        return jsonify({'error': 'Missing required field: books'}), 400
    except Exception as e:
        # Return a 500 Internal Server Error response if an unexpected error occurs
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)