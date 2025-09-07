from pydantic import BaseModel, Field, field_validator
from typing import Literal

import datetime


class BookSchema(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Book title must not be empty")
    author: str = Field(..., min_length=3, max_length=255, description="Author name must be at least 3 characters")
    published_year: int = Field(..., ge=1450, le=datetime.datetime.now().year, description="Year must be realistic")
    genre: Literal['fiction', 'non-fiction', 'science', 'history', 'other']
    available: bool

    # Custom validator for title
    @field_validator("title")
    def title_not_numeric(cls, v):
        if v.isdigit():
            raise ValueError("Title cannot be only numbers")
        return v

    # Custom validator for author
    @field_validator("author")
    def author_no_digits(cls, v):
        if any(char.isdigit() for char in v):
            raise ValueError("Author name cannot contain numbers")
        return v
    
class BookUpdateSchema(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Book title must not be empty")
    author: str = Field(..., min_length=3, max_length=255, description="Author name must be at least 3 characters")
    published_year: int = Field(..., ge=1450, le=datetime.datetime.now().year, description="Year must be realistic")
    genre: Literal['fiction', 'non-fiction', 'science', 'history', 'other']
    available: bool

    # Custom validator for title
    @field_validator("title")
    def title_not_numeric(cls, v):
        if v.isdigit():
            raise ValueError("Title cannot be only numbers")
        return v

    # Custom validator for author
    @field_validator("author")
    def author_no_digits(cls, v):
        if any(char.isdigit() for char in v):
            raise ValueError("Author name cannot contain numbers")
        return v