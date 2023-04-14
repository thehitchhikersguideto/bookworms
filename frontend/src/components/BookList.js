import React, { useState } from 'react';
import './css/book.css';
import RatingPopup from './RatingPopup';

function BookList({ books, onBookRated, isRatedList = false, onRemoveRatedBook }) {
  const [selectedBook, setSelectedBook] = useState(null);
  const [hoveredBook, setHoveredBook] = useState(null);

  const handleBookClick = (book) => {
    if (!isRatedList) {
      setSelectedBook(book);
    }
  };

  const handleRatingSelected = (book, rating) => {
    onBookRated(book, rating);
    setSelectedBook(null);
  };

  const handleRemoveClick = (event, book) => {
    event.stopPropagation();
    onRemoveRatedBook(book);
  };

  return (
    <div className="scrollable-book-list">
      <ul className="book-list">
        {books.map((book) => (
          <li key={book.id} className="book-item">
            <div
              className={`book-block${selectedBook && selectedBook.id === book.id ? ' selected' : ''}`}
              onClick={selectedBook && selectedBook.id === book.id ? null : () => handleBookClick(book)}
              onMouseEnter={isRatedList ? () => setHoveredBook(book) : null}
              onMouseLeave={isRatedList ? () => setHoveredBook(null) : null}
            >
              {isRatedList && hoveredBook && hoveredBook.id === book.id && (
                <button
                  className="remove-rated-book"
                  onClick={(event) => handleRemoveClick(event, book)}
                >
                  Remove
                </button>
              )}
              {selectedBook && selectedBook.id === book.id ? (
                <RatingPopup
                  book={book}
                  onRatingSelected={handleRatingSelected}
                />
              ) : (
                <>
                  {book.image && (
                    <img src={book.image} alt={book.title} className="book-image" />
                  )}
                  <div>
                    <h3 className="book-title">{book.title}</h3>
                    <p className="book-authors">{book.author}</p>
                  </div>
                </>
              )}
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default BookList;