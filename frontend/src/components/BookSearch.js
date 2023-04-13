import React, { useState } from 'react';
import './css/styles.css';
import './css/book.css';
import BookList from './BookList';

export default function BookSearch() {
    const [query, setQuery] = useState('');
    const [books, setBooks] = useState([]);

    const handleInputChange = (event) => {
        setQuery(event.target.value);
    };

    const handleSubmit = async (event) => {
        event.preventDefault();
        const response = await fetch(`/api/search?query=${query}`);
        const data = await response.json();
        const books = data.map((book) => ({
            id: book.id,
            title: book.title,
            authors: book.authors.join(', '),
            image: book.image,
        }));
        setBooks(books);
    };

    return (
        <div className="FormS">
            <h2>Book Recommender</h2>
            <form onSubmit={handleSubmit}>
                <input className="input_book" type="text" value={query} onChange={handleInputChange} placeholder="Search for books" />
            </form>
            <BookList books={books} />
        </div>
    );
}