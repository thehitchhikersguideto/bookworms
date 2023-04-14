import React from 'react';
import './css/recommendedBooks.css';

function RecommendedBooks({ books }) {
  return (
    <div className="recommended-books">
      {books.map((book) => (
        <div key={book.id} className="recommended-book">
          <img src={book.image} alt={book.title} className="recommended-book-image" />
          <h3 className="recommended-book-title">{book.title}</h3>
          <p className="recommended-book-authors">{book.authors}</p>
        </div>
      ))}
    </div>
  );
}

export default RecommendedBooks;
