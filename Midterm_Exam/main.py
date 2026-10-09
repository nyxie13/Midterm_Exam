from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

import models, schemas, crud
from database import engine, get_db

# Automatically verify and build schema structures on startup
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Library Inventory API")



@app.post("/categories/", response_model=schemas.CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category_route(category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    db_category = crud.get_category_by_name(db, name=category.name)
    if db_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category name already exists"
        )
    return crud.create_category(db=db, category=category)


@app.get("/categories/", response_model=List[schemas.CategoryResponse], status_code=status.HTTP_200_OK)
def read_categories_route(db: Session = Depends(get_db)):
    return crud.get_categories(db)



@app.post("/books/", response_model=schemas.BookResponse, status_code=status.HTTP_201_CREATED)
def create_book_route(book: schemas.BookCreate, db: Session = Depends(get_db)):
    # Error Handling validation: Ensure the referenced Category ID exists
    db_category = crud.get_category(db, category_id=book.category_id)
    if not db_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create a book linked to a non-existent category_id"
        )

    # Error Handling validation: Catch duplicate structural constraints
    db_book = crud.get_book_by_isbn(db, isbn=book.isbn)
    if db_book:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Duplicate isbn"
        )

    return crud.create_book(db=db, book=book)


@app.get("/books/", response_model=List[schemas.BookResponse], status_code=status.HTTP_200_OK)
def read_books_route(category_id: Optional[int] = None, db: Session = Depends(get_db)):
    # Optional dynamic parameter query validation
    if category_id is not None:
        db_category = crud.get_category(db, category_id=category_id)
        if not db_category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="category_id does not exist"
            )
    return crud.get_books(db, category_id=category_id)


@app.get("/books/{book_id}", response_model=schemas.BookResponse, status_code=status.HTTP_200_OK)
def read_book_route(book_id: int, db: Session = Depends(get_db)):
    db_book = crud.get_book(db, book_id=book_id)
    if not db_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="book_id does not exist"
        )
    return db_book


@app.put("/books/{book_id}", response_model=schemas.BookResponse, status_code=status.HTTP_200_OK)
def update_book_route(book_id: int, book_update: schemas.BookUpdate, db: Session = Depends(get_db)):
    db_book = crud.get_book(db, book_id=book_id)
    if not db_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="book_id does not exist"
        )

    # Check relational model keys gracefully if modified
    if book_update.category_id is not None:
        db_category = crud.get_category(db, category_id=book_update.category_id)
        if not db_category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="category_id does not exist"
            )

    # Check unique constraints if an updated ISBN is supplied
    if book_update.isbn is not None and book_update.isbn != db_book.isbn:
        isbn_check = crud.get_book_by_isbn(db, isbn=book_update.isbn)
        if isbn_check:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Duplicate isbn"
            )

    return crud.update_book(db=db, db_book=db_book, book_update=book_update)


@app.delete("/books/{book_id}", status_code=status.HTTP_200_OK)
def delete_book_route(book_id: int, db: Session = Depends(get_db)):
    db_book = crud.get_book(db, book_id=book_id)
    if not db_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="book_id does not exist"
        )
    crud.delete_book(db=db, db_book=db_book)
    return {"detail": "Book removed successfully from inventory"}