from fastapi import FastAPI

import uvicorn

from crud import books

app = FastAPI()

app.include_router("/books", books)


if __name__ == "__main__":
    print("awad")
