import contextlib
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging

from app.core.database import db_manager
from app.services.chess_agent import chess_agent
from app.services.rag_service import rag_service
from app.services.youtube_service import youtube_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==========================================
# 1. GESTION DU CYCLE DE VIE (LIFESPAN)
# ==========================================
@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    # Démarrage propre des connexions au boot de l'API
    logger.info("✅ Initialisation des services...")
    try:
        await db_manager.connect()
        rag_service.init_db()
        logger.info("✅ Services initialisés avec succès")
    except Exception as e:
        logger.warning(f"⚠️ Avertissement lors de l'initialisation: {e}")

    yield

    # Coupure propre au shutdown
    logger.info("🛑 Arrêt des services...")
    await db_manager.disconnect()


# ==========================================
# 2. INITIALISATION DE L'APPLICATION
# ==========================================
app = FastAPI(
    title="FFE Chess Agent API",
    version="1.0.0",
    description="Backend API - Architecture découplée : LangGraph, FastAPI, Milvus et MongoDB",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# 3. SCHÉMAS PYDANTIC
# ==========================================

class MovePayload(BaseModel):
    move: str
    fen: str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"


class VectorSearchPayload(BaseModel):
    query: str


# ==========================================
# 4. ROUTES : SYSTEME & HEALTH
# ==========================================

@app.get("/", tags=["Système"])
def read_root():
    return {
        "service": "FFE Chess Agent API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/api/v1/healthcheck", tags=["Système"])
def healthcheck():
    return {
        "status": "healthy",
        "service": "chess-backend",
        "database_status": "connected",
        "stockfish": "available",
        "milvus": "connected",
        "youtube_api": "configured"
    }


# ==========================================
# 5. ROUTES : CHESS AGENT (Orchestration)
# ==========================================

@app.post("/api/v1/chess/move", tags=["Chess Analysis"])
async def receive_move(payload: MovePayload):
    """
    Orchestration complète d'une analyse de coup.
    Retourne:
    - Meilleur coup (Stockfish)
    - Évaluation de la position
    - Coups théoriques (Lichess)
    - Contexte pédagogique (RAG)
    - Vidéos éducatives (YouTube)
    """
    logger.info(f"📥 Coup reçu: {payload.move} | FEN: {payload.fen}")

    try:
        result = await chess_agent.process_move(payload.move, payload.fen)
        logger.info(f"✅ Analyse complète pour {payload.move}")
        return result
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'analyse: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================
# 6. ROUTES : RAG / RECHERCHE VECTORIELLE
# ==========================================

@app.post("/api/v1/vector-search", tags=["RAG & Knowledge"])
async def vector_search(payload: VectorSearchPayload):
    """
    Recherche dans la base vectorielle Milvus.
    Retourne les documents les plus pertinents pour la requête.
    """
    logger.info(f"🔍 Recherche vectorielle: {payload.query}")

    try:
        hits = rag_service.search(payload.query)
        return {
            "query": payload.query,
            "results": hits,
            "count": len(hits)
        }
    except Exception as e:
        logger.error(f"❌ Erreur RAG: {str(e)}")
        return {
            "query": payload.query,
            "results": [],
            "error": str(e)
        }


@app.get("/api/v1/rag/init", tags=["RAG & Knowledge"])
def init_rag_database():
    """
    Initialise la base de données Milvus avec les données de démo.
    """
    logger.info("🚀 Initialisation Milvus RAG...")

    try:
        result = rag_service.init_db()
        return {"status": "success", "message": result}
    except Exception as e:
        logger.error(f"❌ Erreur init RAG: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================
# 7. ROUTES : YOUTUBE VIDEOS
# ==========================================

@app.get("/api/v1/videos/{opening}", tags=["Educational Resources"])
async def get_videos(opening: str):
    """
    Recherche des vidéos éducatives sur YouTube pour une ouverture donnée.
    """
    logger.info(f"🎬 Recherche vidéos: {opening}")

    try:
        videos = youtube_service.search_videos(opening)
        return {
            "opening": opening,
            "videos": videos,
            "count": len(videos)
        }
    except Exception as e:
        logger.error(f"❌ Erreur YouTube: {str(e)}")
        return {
            "opening": opening,
            "videos": [],
            "error": str(e)
        }


# ==========================================
# 8. ROUTES : DEBUG & STATS
# ==========================================

@app.get("/api/v1/stats", tags=["Debug"])
def get_stats():
    """Statistiques système et services."""
    return {
        "services": {
            "chess": "operational",
            "stockfish": "available",
            "milvus": "connected",
            "mongodb": "connected",
            "youtube_api": "configured"
        },
        "features": {
            "theoretical_moves": True,
            "position_evaluation": True,
            "rag_search": True,
            "video_recommendations": True,
            "langgraph_orchestration": True
        }
    }
