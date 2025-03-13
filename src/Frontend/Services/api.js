import axios from 'axios';

const API_URL = "https://your-fastapi-backend.onrender.com";

export const fetchBooks = async () => {
  const response = await axios.get(`${API_URL}/books/`);
  return response.data;
};
