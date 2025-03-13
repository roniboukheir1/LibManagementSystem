from fastapi import FastAPI, Depends, HTTPException
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session
from database import init_db, SessionLocal
from models import Book, Transaction, User
from passlib.context import CryptContext
from pydantic import BaseModel
from typing import List
import uvicorn

app = FastAPI()
init_db()

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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)