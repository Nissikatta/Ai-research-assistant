from fastapi import FastAPI

from app.routers import (
    documents,
    qa,
    search,
    classifier,
    analysis,
    analytics,
)

app = FastAPI(
    title="AI Research & Knowledge Assistant",
    version="1.0.0"
)

@app.get("/")
def home():
    return {"message": "AI Research Assistant API is running"}

app.include_router(documents.router)
app.include_router(qa.router)
app.include_router(search.router)
app.include_router(classifier.router)
app.include_router(analysis.router)
app.include_router(analytics.router)