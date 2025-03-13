import React, { useEffect, useState } from "react";
import axios from "axios";

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

function App() {
  const [books, setBooks] = useState([]);
  const [title, setTitle] = useState("");
  const [author, setAuthor] = useState("");
  const [genre, setGenre] = useState("");

  useEffect(() => {
    fetchBooks();
  }, []);

  const fetchBooks = async () => {
    const response = await axios.get(`${API_URL}/books/`);
    setBooks(response.data);
  };

  const addBook = async () => {
    if (!title || !author || !genre) return alert("All fields are required!");
    await axios.post(`${API_URL}/books/`, { title, author, genre });
    fetchBooks();
    setTitle("");
    setAuthor("");
    setGenre("");
  };

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center p-6">
      <h1 className="text-3xl font-bold text-blue-600 mb-4">📚 Library Management System</h1>

      {/* Add Book Form */}
      <div className="bg-white p-4 rounded-lg shadow-md w-96 mb-6">
        <h2 className="text-xl font-semibold mb-2">Add a New Book</h2>
        <input
          className="w-full p-2 border rounded mb-2"
          placeholder="Title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
        />
        <input
          className="w-full p-2 border rounded mb-2"
          placeholder="Author"
          value={author}
          onChange={(e) => setAuthor(e.target.value)}
        />
        <input
          className="w-full p-2 border rounded mb-2"
          placeholder="Genre"
          value={genre}
          onChange={(e) => setGenre(e.target.value)}
        />
        <button
          onClick={addBook}
          className="bg-blue-500 text-white px-4 py-2 rounded w-full hover:bg-blue-600"
        >
          Add Book
        </button>
      </div>

      {/* Book List */}
      <div className="w-full max-w-2xl">
        <h2 className="text-2xl font-semibold mb-2">Available Books</h2>
        <ul className="bg-white shadow-lg rounded-lg p-4">
          {books.length > 0 ? (
            books.map((book) => (
              <li key={book.id} className="border-b py-2 flex justify-between">
                <span>
                  <strong>{book.title}</strong> by {book.author} ({book.genre})
                </span>
              </li>
            ))
          ) : (
            <p className="text-gray-500">No books available.</p>
          )}
        </ul>
      </div>
    </div>
  );
}

export default App;
