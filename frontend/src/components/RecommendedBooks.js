import React from 'react';
import './css/book.css';

function RecommendedBooks({ books }) {
  return (
    <div className="recommended-books">
      <div className="scrollable-book-list">
        <ul className="book-list">
          {books.map((book) => (
            <li key={book.id} className="book-item">
              <a href={book.link} target="_blank" rel="noopener noreferrer" className="book-block">
                <img src={book.image} alt={"No IMG"} className="book-image" />
                <h3 className="book-title">{book.title}</h3>
                <p className="book-authors">{book.author}</p>
              </a>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export default RecommendedBooks;