"""
Palabam FastAPI Backend
Main entry point for the vocabulary learning platform API
"""
import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Configure logging to stdout (App Runner captures this)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Create app FIRST - no lifespan to avoid blocking
# Log startup info immediately
logger.info("=" * 50)
logger.info("Starting Palabam API...")
logger.info(f"PORT environment variable: {os.getenv('PORT', 'not set')}")
logger.info("Health endpoint is available immediately")
logger.info("=" * 50)

app = FastAPI(
    title="Palabam API",
    description="Personalized Vocabulary Recommendation Engine API",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health endpoints - available immediately, no imports needed
@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Palabam API is running", "version": "2.0.0"}

@app.get("/health")
async def health():
    """Health check endpoint - must respond quickly"""
    return {"status": "healthy", "port": os.getenv("PORT", "8080")}

def load_routers():
    """Load all routers - called during startup"""
    # Import routers with error handling
    try:
        logger.info("Loading NLP routers...")
        from nlp import profiler, recommender
        app.include_router(profiler.router, prefix="/api/profile", tags=["profiling"])
        app.include_router(recommender.router, prefix="/api/recommend", tags=["recommendations"])
        logger.info("✓ NLP routers loaded successfully")
    except Exception as e:
        logger.error(f"✗ Failed to load NLP routers: {e}", exc_info=True)

    # Story Spark routers
    try:
        logger.info("Loading API routers...")
        from api import classes, submissions, students, test_setup, chatbot, parents, invites, users
        app.include_router(classes.router, prefix="/api/classes", tags=["classes"])
        app.include_router(submissions.router, prefix="/api/submissions", tags=["submissions"])
        app.include_router(students.router, prefix="/api/students", tags=["students"])
        app.include_router(parents.router, prefix="/api/parents", tags=["parents"])
        app.include_router(invites.router, prefix="/api/invites", tags=["invites"])
        app.include_router(users.router, prefix="/api/users", tags=["users"])
        app.include_router(test_setup.router, prefix="/api/test", tags=["testing"])
        app.include_router(chatbot.router, prefix="/api/chatbot", tags=["chatbot"])
        logger.info("✓ API routers loaded successfully")
    except Exception as e:
        logger.error(f"✗ Failed to load API routers: {e}", exc_info=True)

# Load routers after app is created
# Health endpoint is already registered, so app can start even if routers fail
try:
    load_routers()
    logger.info("Application initialization complete")
except Exception as e:
    logger.error(f"Error during router loading (app will still start): {e}", exc_info=True)
    logger.info("Application starting with health endpoint only")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

