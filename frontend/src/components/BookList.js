import React from 'react';
import './css/book.css'

function BookList({ books }) {
    return (
        <ul className="book-list">
            {books.map((book) => (
                <li key={book.id} className="book-item">
                    {book.image && <img src={book.image} alt={book.title} className="book-image" />}
                    <div>
                        <h3 className="book-title">{book.title}</h3>
                        <p className="book-authors">{book.authors}</p>
                    </div>
                </li>
            ))}
        </ul>
    );
}

export default BookList;