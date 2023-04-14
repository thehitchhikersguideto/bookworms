import React, { useState } from 'react';
import './css/styles.css';
import './css/book.css';
import BookList from './BookList';
import RecommendedBooks from './RecommendedBooks';
import RecommenderButton from './RecommenderButton';

export default function BookSearch() {
  const apiurl = `${process.env.REACT_APP_API_URL}`;
  const [query, setQuery] = useState('');
  const [books, setBooks] = useState([]);
  const [error, setError] = useState(null);
  const [ratedBooks, setRatedBooks] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [showRecommendations, setShowRecommendations] = useState(false);

  const handleBookRated = (book, rating) => {
    setRatedBooks((prevRatedBooks) => [
      ...prevRatedBooks,
      { ...book, rating },
    ]);
  };

  const handleRemoveRatedBook = (bookToRemove) => {
    setRatedBooks((prevRatedBooks) => prevRatedBooks.filter((book) => book.id !== bookToRemove.id));
  };

  const handleInputChange = (event) => {
    setQuery(event.target.value);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError(null);

    try {
      const response = await fetch(`${apiurl}/api/search?query=${query}`);

      if (!response.ok) {
        throw new Error('Failed to retrieve books');
      }

      const data = await response.json();
      console.log('Parsed response:', data);
      const books = data.map((book) => ({
        id: book.id,
        title: book.title,
        author: book.author,
        image: book.image,
      }));
      setBooks(books);
    } catch (err) {
      setError(err.message);
    }
  };

  const filteredBooks = books.filter(
    (book) => !ratedBooks.some((ratedBook) => ratedBook.id === book.id)
  );

  return (
    <div className="FormS">
      {showRecommendations ? (
        <RecommendedBooks books={recommendations} />
      ) : (
        <>
          <h2>Book Recommender</h2>
          <form onSubmit={handleSubmit}>
            <input
              className="input_book"
              type="text"
              value={query}
              onChange={handleInputChange}
              placeholder="Search for books"
            />
          </form>
          {ratedBooks.length > 0 && (
            <>
              <h3>Your Rated Books</h3>
              <BookList
                books={ratedBooks}
                onBookRated={handleBookRated}
                isRatedList={true}
                onRemoveRatedBook={handleRemoveRatedBook}
              />
              <RecommenderButton ratedBooks={ratedBooks} />
            </>
          )}
          {error ? (
            <div className="error">{error}</div>
            ) : (
            <BookList
                       books={filteredBooks}
                       onBookRated={handleBookRated}
                     />
    )}
    </>
    )}
        </div>
    );
    }
