"""
Palabam FastAPI Backend
Main entry point for the vocabulary learning platform API
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

app = FastAPI(
    title="Palabam API",
    description="AI-Powered Vocabulary Odyssey API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Palabam API is running", "version": "1.0.0"}

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}

# Import routers
from nlp import profiler, recommender, srs
app.include_router(profiler.router, prefix="/api/profile", tags=["profiling"])
app.include_router(recommender.router, prefix="/api/recommend", tags=["recommendations"])
app.include_router(srs.router, prefix="/api/srs", tags=["srs"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

