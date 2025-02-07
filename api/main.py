from fastapi import FastAPI
from api.endpoints import text, pdf

app = FastAPI()

app.include_router(text.router, prefix="/text")
app.include_router(pdf.router, prefix="/pdf")
