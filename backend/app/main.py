import contextlib
from fastapi import FastAPI, Query, HTTPException

# ==========================================
# 1. GESTION DU CYCLE DE VIE (LIFESPAN)
# ==========================================
@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gère les actions au démarrage et à la fermeture de l'application.
    Utile pour orchestrer les futures connexions à Milvus sans bloquer l'API.
    """
    print("🚀 [STARTUP] Démarrage de l'agent Chess... Initialisation des services.")
    yield
    print("🛑 [SHUTDOWN] Fermeture de l'agent Chess... Libération des ressources.")


# ==========================================
# 2. INITIALISATION DE L'APPLICATION
# ==========================================
app = FastAPI(
    title="FFE Chess Agent API",
    version="1.0.0",
    description="Backend API - Étape 4 : Intégration RAG, Milvus & YouTube API",
    lifespan=lifespan
)


# ==========================================
# 3. ROUTES : SYSTEME & FONDAMENTAUX
# ==========================================

@app.get("/", tags=["Système"])
def read_root():
    """Route racine 'Hello World' pour valider le statut du conteneur."""
    return {
        "message": "Hello World from FastAPI!",
        "docs": "/docs"
    }


@app.get("/api/v1/healthcheck", tags=["Système"])
def healthcheck():
    """Route de vérification demandée pour s'assurer du bon fonctionnement de l'API."""
    return {
        "status": "healthy",
        "service": "chess-backend",
        "milvus_status": "pending_connection"
    }


# ==========================================
# 4. ROUTES : ANALYSE & JEU
# ==========================================

@app.get("/api/v1/moves", tags=["Analyse & Jeu"])
def get_moves(
    fen: str = Query(..., description="La position actuelle de l'échiquier au format FEN"),
    query: str = Query(None, description="Filtrage sémantique textuel optionnel (ex: 'sicilienne')")
):
    """
    Récupère les suggestions de coups basées sur une position FEN (obligatoire)
    et une recherche sémantique textuelle (optionnelle).
    """
    if not fen or fen.strip() == "":
        raise HTTPException(
            status_code=400, 
            detail="Le paramètre 'fen' est obligatoire et ne peut pas être vide."
        )
        
    return {
        "fen_received": fen,
        "query_received": query,
        "suggested_moves": [
            {"move": "e2e4", "score": 0.91, "opening": "King's Pawn Game"},
            {"move": "c7c5", "score": 0.88, "opening": "Sicilian Defense"}
        ]
    }


# ==========================================
# 5. ROUTES : RAG & CONNAISSANCE (SEARCH)
# ==========================================

@app.get("/api/v1/vector-search", tags=["RAG & Connaissance"])
def vector_search(
    query: str = Query(..., description="Le concept ou l'ouverture à rechercher s'émantiquement")
):
    """
    Effectue une recherche vectorielle sémantique dans la base de données Milvus
    pour en extraire des connaissances théoriques sur les échecs.
    """
    if not query or query.strip() == "":
        raise HTTPException(
            status_code=400,
            detail="Le paramètre 'query' est requis pour effectuer une recherche vectorielle."
        )

    # Simulation en attendant le raccordement du client Milvus complet
    return {
        "query": query,
        "database": "milvus",
        "results": [
            {
                "id": 1024,
                "document": "La défense sicilienne est caractérisée par les coups 1.e4 c5...",
                "similarity_score": 0.94
            }
        ]
    }


# ==========================================
# 6. ROUTES : RESSOURCES PEDAGOGIQUES (VIDEO)
# ==========================================

@app.get("/api/v1/videos/{opening}", tags=["Ressources Pédagogiques"])
def get_opening_videos(
    opening: str,
    max_results: int = Query(5, ge=1, le=50, description="Nombre maximum de vidéos à retourner")
):
    """
    Récupère des ressources pédagogiques vidéo (via YouTube Data API v3) 
    associées à une ouverture spécifique passée en paramètre de chemin.
    """
    if not opening or opening.strip() == "":
        raise HTTPException(
            status_code=400,
            detail="Le nom de l'ouverture est obligatoire."
        )

    # Simulation en attendant la réintégration de ton script d'authentification YouTube
    return {
        "opening_queried": opening,
        "max_results": max_results,
        "videos": [
            {
                "video_id": "dQw4w9WgXcQ",
                "title": f"Maîtriser l'ouverture : {opening}",
                "channel_name": "Chess Masters TV",
                "published_at": "2026-01-15T10:00:00Z"
            }
        ]
    }