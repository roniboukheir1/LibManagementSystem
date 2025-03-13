import React, { useEffect, useState } from 'react';
import { fetchBooks } from '../services/api';

function App() {
  const [books, setBooks] = useState([]);

  useEffect(() => {
    fetchBooks().then(data => setBooks(data));
  }, []);

  return (
    <div>
      <h1>Library Management System</h1>
      <ul>
        {books.map((book) => (
          <li key={book.id}>{book.title} by {book.author}</li>
        ))}
      </ul>
    </div>
  );
}

export default App;