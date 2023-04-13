import React, { useState } from 'react';
import './css/styles.css';
import './css/book.css';
import BookList from './BookList';

export default function BookSearch() {
  const [query, setQuery] = useState('');
  const [books, setBooks] = useState([]);
  const [error, setError] = useState(null);

  const handleInputChange = (event) => {
    setQuery(event.target.value);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError(null);

    try {
      const response = await fetch(`/api/search?query=${query}`);
      console.log('Raw response:', response); // Add this line to log the raw response

      if (!response.ok) {
        throw new Error('Failed to retrieve books');
      }

      const data = await response.json();
      console.log('Parsed response:', data); // Add this line to log the parsed response
      const books = data.map((book) => ({
        id: book.id,
        title: book.title,
        authors: book.authors.join(', '),
        image: book.image,
      }));
      setBooks(books);
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="FormS">
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
      {error ? (
        <div className="error">{error}</div>
      ) : (
        <BookList books={books} />
      )}
    </div>
  );
}
