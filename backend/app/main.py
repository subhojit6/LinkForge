import re
import secrets
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl

class ShortenRequest(BaseModel):
    original_url: HttpUrl
    custom_alias: str | None = None

url_store = {}

def generate_short_code():
    short_code = secrets.token_urlsafe(4)[:6]
    while short_code in url_store:
        short_code = secrets.token_urlsafe(4)[:6]
    return short_code

# Create our FastAPI application
app = FastAPI(
    title="LinkForge",
    description="A URL Shortener Application",
    version="1.0.0"
)

# Root endpoint
@app.get("/")
def home():
    return {
        "message": "Welcome to LinkForge!",
        "status": "running"
    }

# Health check endpoint
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "application": "LinkForge"
    }

@app.post("/shorten", status_code=status.HTTP_201_CREATED)
def shorten_url(request: ShortenRequest):
    if request.custom_alias:
        if not re.fullmatch(r"[a-zA-Z0-9_-]+", request.custom_alias):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Alias can only contain letters, numbers, hyphens, and underscores")
        if request.custom_alias in url_store:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Custom alias already exists.")
        short_code = request.custom_alias
    else:
        short_code = generate_short_code()
    url_store[short_code] = str(request.original_url)
    return {
        "original_url" : str(request.original_url),
        "short_code": short_code,
        "short_url" : f"http://127.0.0.1:8000/{short_code}"
    }

@app.get("/{short_code}")
def redirect_url(short_code: str):
    if short_code not in url_store:
        raise HTTPException(status_code=404, detail="Short URL not found")
    return RedirectResponse(url_store[short_code])

