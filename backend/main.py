from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field, field_validator
import time

app = FastAPI(
    title="Digital Library API",
    description="A RESTful API to manage a digital library",
    version="1.0.0"
)

booksDB = []

class Book(BaseModel):
    id: int
    title: str = Field(..., min_length=1)
    author: str
    year: int = Field(..., ge=1000, le=2026)
    isbn: str

    @field_validator("isbn")
    def validate_isbn(cls, value):
        if len(value) not in (10, 13):
            raise ValueError("ISBN must be 10 or 13 characters long")
        return value

@app.middleware("http")
async def log_requests(request: Request, call_next):
    startTime = time.time()

    userAgent = request.headers.get("user-agent", "Unknown")
    print(f"[LOG] Request received from: {userAgent}")

    response = await call_next(request)

    timeTaken = time.time() - startTime
    response.headers["X-Process-Time"] = str(timeTaken)

    return response

@app.post(
    "/books",
    tags=["Library"],
    summary="Add a new book",
    description="Adds a new book to the digital library"
)
def add_book(book: Book):
    for b in booksDB:
        if b["id"] == book.id:
            raise HTTPException(
                status_code=400,
                detail="Book with this ID already exists"
            )
    booksDB.append(book.model_dump())
    return book


@app.get(
    "/books",
    tags=["Library"],
    summary="Get all books",
    description="Retrieve all books from the library"
)
def get_all_books():
    return booksDB


@app.get(
    "/books/{book_id}",
    tags=["Library"],
    summary="Get book by ID",
    description="Retrieve a specific book using its ID"
)
def get_book_by_id(book_id: int):
    for book in booksDB:
        if book["id"] == book_id:
            return book
    raise HTTPException(status_code=404, detail="Book not found")


@app.put(
    "/books/{book_id}",
    tags=["Library"],
    summary="Update a book",
    description="Update details of an existing book"
)
def update_book(book_id: int, updated_book: Book):
    for index, book in enumerate(booksDB):
        if book["id"] == book_id:
            booksDB[index] = updated_book.dict()
            return updated_book
    raise HTTPException(status_code=404, detail="Book not found")


@app.delete(
    "/books/{book_id}",
    tags=["Library"],
    summary="Delete a book",
    description="Remove a book from the library"
)
def delete_book(book_id: int):
    for book in booksDB:
        if book["id"] == book_id:
            booksDB.remove(book)
            return {"message": "Book deleted successfully"}
    raise HTTPException(status_code=404, detail="Book not found")
