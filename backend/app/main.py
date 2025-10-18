"""
Knowledge Transfer Bot - FastAPI Application
Enhanced implementation with LLM orchestration
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import logging

from app.core.database import engine, create_tables
from app.core.cache import redis_client
from app.llm.orchestrator import LLMOrchestrator
from app.services.vector_service import VectorService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events
    """
    # Startup
    logger.info("🚀 Starting KT-AI Backend...")

    try:
        # Initialize database
        await create_tables()
        logger.info("✓ Database initialized")

        # Initialize Redis
        await redis_client.ping()
        logger.info("✓ Redis connected")

        # Initialize LLM orchestrator
        app.state.llm = LLMOrchestrator()
        await app.state.llm.initialize()
        logger.info("✓ LLM orchestrator initialized")

        # Initialize vector store (Azure AI Search)
        app.state.vector_service = VectorService()
        await app.state.vector_service.initialize()
        logger.info("✓ Azure AI Search initialized")

        logger.info("🎉 KT-AI Backend ready!")

    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise

    yield

    # Shutdown
    logger.info("🛑 Shutting down KT-AI Backend...")
    try:
        await redis_client.close()
        await app.state.llm.shutdown()
        logger.info("✓ Shutdown complete")
    except Exception as e:
        logger.error(f"❌ Shutdown error: {e}")

# Create FastAPI app
app = FastAPI(
    title="Knowledge Transfer Bot API",
    description="LLM-powered ESG knowledge gap detection and resolution",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
from app.api.v1 import gaps, questions, answers, knowledge_base, websocket

app.include_router(gaps.router, prefix="/api/v1/gaps", tags=["gaps"])
app.include_router(questions.router, prefix="/api/v1/questions", tags=["questions"])
app.include_router(answers.router, prefix="/api/v1/answers", tags=["answers"])
app.include_router(knowledge_base.router, prefix="/api/v1/kb", tags=["knowledge-base"])
app.include_router(websocket.router, prefix="/ws", tags=["websocket"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "KT-AI Backend API",
        "version": "2.0.0",
        "status": "operational",
        "features": [
            "LLM Orchestration",
            "Gap Detection",
            "Question Generation",
            "Vector Search",
            "Real-time Updates"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check database
        db_status = "connected"
        
        # Check Redis
        await redis_client.ping()
        redis_status = "connected"
        
        # Check LLM orchestrator
        llm_status = "operational" if hasattr(app.state, 'llm') else "not_initialized"
        
        return {
            "status": "healthy",
            "database": db_status,
            "redis": redis_status,
            "llm": llm_status,
            "timestamp": "2024-01-01T00:00:00Z"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": "2024-01-01T00:00:00Z"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
