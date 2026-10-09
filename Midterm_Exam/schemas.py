from pydantic import BaseModel, ConfigDict
from typing import Optional

class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class BookBase(BaseModel):
    title: str
    isbn: str
    publication_year: Optional[int] = None
    stock_quantity: Optional[int] = 1
    category_id: int

class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    title: Optional[str] = None
    isbn: Optional[str] = None
    publication_year: Optional[int] = None
    stock_quantity: Optional[int] = None
    category_id: Optional[int] = None

class BookResponse(BookBase):
    id: int

    model_config = ConfigDict(from_attributes=True)