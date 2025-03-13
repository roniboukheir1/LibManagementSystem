from fastapi import FastAPI, Depends, HTTPException
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session
from .database import init_db, SessionLocal
from .models import Book, Transaction, User
from passlib.context import CryptContext
from pydantic import BaseModel
from typing import List
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = FastAPI()
init_db()

# Enable CORS for Frontend Requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = SessionLocal()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Settings:
    authjwt_secret_key: str = "supersecret"

@AuthJWT.load_config
def get_config():
    return Settings()

class UserLogin(BaseModel):
    username: str
    password: str

class BookCreate(BaseModel):
    title: str
    author: str
    genre: str

@app.post("/register")
def register(user: UserLogin, db: Session = Depends(SessionLocal)):
    hashed_password = pwd_context.hash(user.password)
    db_user = User(username=user.username, password_hash=hashed_password)
    db.add(db_user)
    db.commit()
    return {"msg": "User registered"}

@app.post("/login")
def login(user: UserLogin, db: Session = Depends(SessionLocal), Authorize: AuthJWT = Depends()):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not pwd_context.verify(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = Authorize.create_access_token(subject=db_user.username)
    return {"access_token": access_token}

@app.post("/books/")
def create_book(book: BookCreate, db: Session = Depends(SessionLocal)):
    db_book = Book(title=book.title, author=book.author, genre=book.genre)
    db.add(db_book)
    db.commit()
    return db_book

@app.get("/books/", response_model=List[BookCreate])
def get_books(db: Session = Depends(SessionLocal)):
    return db.query(Book).all()

@app.post("/books/borrow/{book_id}")
def borrow_book(book_id: int, db: Session = Depends(SessionLocal)):
    book = db.query(Book).filter(Book.id == book_id, Book.available == True).first()
    if not book:
        raise HTTPException(status_code=400, detail="Book not available")

    book.available = False
    transaction = Transaction(book_id=book.id, action="borrow")
    db.add(transaction)
    db.commit()
    return {"msg": "Book borrowed successfully"}

@app.post("/books/return/{book_id}")
def return_book(book_id: int, db: Session = Depends(SessionLocal)):
    book = db.query(Book).filter(Book.id == book_id, Book.available == False).first()
    if not book:
        raise HTTPException(status_code=400, detail="Book is not borrowed")

    book.available = True
    transaction = Transaction(book_id=book.id, action="return")
    db.add(transaction)
    db.commit()
    return {"msg": "Book returned successfully"}

# AI: Recommend Books Based on User Borrowing History
@app.get("/recommend/{user_id}")
def recommend_books(user_id: int, db: Session = Depends(SessionLocal)):
    user_transactions = db.query(Transaction).filter(Transaction.user_id == user_id).all()
    user_history = [db.query(Book).filter(Book.id == t.book_id).first().title for t in user_transactions]
    all_books = db.query(Book).all()
    
    if not user_history or not all_books:
        raise HTTPException(status_code=400, detail="Not enough data for recommendations")

    book_texts = [book.title + " " + book.author + " " + book.genre for book in all_books]
    vectorizer = TfidfVectorizer()
    book_vectors = vectorizer.fit_transform(book_texts)
    user_vector = vectorizer.transform([" ".join(user_history)])

    scores = cosine_similarity(user_vector, book_vectors)[0]
    recommended_books = [all_books[i] for i in scores.argsort()[-5:][::-1]]
    
    return [{"title": book.title, "author": book.author, "genre": book.genre} for book in recommended_books]

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
