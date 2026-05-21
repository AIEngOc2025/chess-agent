from pydantic import BaseModel, Field
from typing import List, Optional

class VideoSuggestion(BaseModel):
    video_id: str
    title: str
    description: str
    channel_name: str
    thumbnail_url: str
    video_url: str
    embed_url: str

class ChessAnalysisResponse(BaseModel):
    fen: str = Field(..., description="La chaîne FEN de la position analysée")
    last_move: Optional[str] = Field("", description="Le dernier coup joué")
    opening_name: str = Field(..., description="Nom de l'ouverture identifiée")
    legal_moves: List[str] = Field(..., description="Liste des coups légaux possibles")
    context_found: List[str] = Field(..., description="Contexte pédagogique sur la position")
    suggested_videos: List[VideoSuggestion] = Field(..., description="Vidéos YouTube recommandées")
    stockfish_eval: str = Field(..., description="Évaluation brute provenant de Stockfish")
    response: str = Field(..., description="Résumé textuel mis en forme pour l'utilisateur")

class EvaluationResponse(BaseModel):
    evaluation: str = Field(..., description="Évaluation de la position (ex: +0.39)")
    best_move: str = Field(..., description="Meilleur coup calculé par le moteur")
    turn: str = Field(..., description="Le trait (white ou black)")
