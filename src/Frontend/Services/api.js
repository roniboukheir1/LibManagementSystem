import axios from "axios";

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

export const fetchBooks = async () => {
  const response = await axios.get(`${API_URL}/books/`);
  return response.data;
};

export const addBook = async (book) => {
  await axios.post(`${API_URL}/books/`, book);
};
