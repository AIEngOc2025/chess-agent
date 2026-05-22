import json
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from app.services.chess_service import chess_service
from app.services.rag_service import rag_service
from app.services.youtube_service import youtube_service

# ==========================================
# 1. DÉFINITION DU STATE (Flux de données)
# ==========================================
class AgentState(TypedDict):
    move: str
    fen: str
    theoretical_moves: dict
    evaluation: dict
    rag_context: list
    videos: list
    analysis_complete: bool

# ==========================================
# 2. NŒUDS DE TRAITEMENT (Workers)
# ==========================================

async def extract_move(state: AgentState) -> AgentState:
    """Extraction et validation du coup UCI."""
    state["analysis_complete"] = False
    print(f"📥 Coup UCI reçu: {state['move']}")
    return state

async def fetch_theoretical_moves(state: AgentState) -> AgentState:
    """Interroge Lichess Explorer pour les coups théoriques."""
    print(f"🎯 Recherche coups théoriques...")
    result = chess_service.get_theoretical_moves(state.get("fen", "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"))
    state["theoretical_moves"] = result
    return state

async def evaluate_position(state: AgentState) -> AgentState:
    """Évalue la position avec Stockfish."""
    print(f"⚖️ Évaluation Stockfish...")
    result = chess_service.evaluate_position_stockfish(state.get("fen", "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"))
    state["evaluation"] = result
    return state

async def search_knowledge_base(state: AgentState) -> AgentState:
    """Interroge Milvus pour obtenir du contexte historique/pédagogique."""
    print(f"📚 Recherche RAG (Milvus)...")
    query = state.get("move", "opening strategy")
    hits = rag_service.search(query)
    state["rag_context"] = hits
    return state

async def find_educational_videos(state: AgentState) -> AgentState:
    """Recherche des vidéos YouTube pertinentes."""
    print(f"🎬 Recherche vidéos YouTube...")
    # Extraction du nom de l'ouverture depuis le contexte RAG si disponible
    opening_name = "chess opening"
    if state["rag_context"] and len(state["rag_context"]) > 0:
        opening_name = state["rag_context"][0].get("opening", "chess opening")

    videos = youtube_service.search_videos(opening_name)
    state["videos"] = videos
    return state

async def compile_analysis(state: AgentState) -> AgentState:
    """Compile tous les résultats en une réponse synthétique."""
    print(f"✅ Compilation de l'analyse...")
    state["analysis_complete"] = True
    return state

# ==========================================
# 3. CONSTRUCTION DU GRAPH LANGGRAPH
# ==========================================

def build_chess_agent_graph():
    """Construit le workflow LangGraph orchestrant tous les services."""
    graph = StateGraph(AgentState)

    # Ajout des nœuds (workers)
    graph.add_node("extract", extract_move)
    graph.add_node("theoretical", fetch_theoretical_moves)
    graph.add_node("evaluate", evaluate_position)
    graph.add_node("rag", search_knowledge_base)
    graph.add_node("videos", find_educational_videos)
    graph.add_node("compile", compile_analysis)

    # Définition du flux (edges)
    graph.add_edge(START, "extract")
    graph.add_edge("extract", "theoretical")
    graph.add_edge("extract", "evaluate")
    graph.add_edge("extract", "rag")
    graph.add_edge("theoretical", "compile")
    graph.add_edge("evaluate", "compile")
    graph.add_edge("rag", "videos")
    graph.add_edge("videos", "compile")
    graph.add_edge("compile", END)

    return graph.compile()

# ==========================================
# 4. SERVICE CHESS AGENT ORCHESTRATEUR
# ==========================================

class ChessAgentService:
    def __init__(self):
        self.graph = build_chess_agent_graph()

    async def process_move(self, move: str, fen: str = None) -> dict:
        """
        Orchestration complète d'une requête utilisateur.
        Retourne une analyse synthétique comprenant:
        - Meilleur coup suggéré
        - Évaluation de la position
        - Contexte pédagogique (RAG)
        - Ressources vidéo
        """
        if not fen:
            fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

        print(f"\n{'='*50}")
        print(f"🔄 DÉMARRAGE ANALYSE - Coup: {move}")
        print(f"{'='*50}\n")

        # État initial pour le workflow
        initial_state = {
            "move": move,
            "fen": fen,
            "theoretical_moves": {},
            "evaluation": {},
            "rag_context": [],
            "videos": [],
            "analysis_complete": False
        }

        # Exécution du graph
        final_state = await self.graph.ainvoke(initial_state)

        # Compilation de la réponse
        response = {
            "move_requested": move,
            "best_move": final_state["evaluation"].get("best_move", "N/A"),
            "evaluation": final_state["evaluation"].get("evaluation", 0),
            "depth": final_state["evaluation"].get("depth", 0),
            "theoretical_moves": [
                m.get("san", m.get("uci", ""))
                for m in final_state["theoretical_moves"].get("moves", [])[:3]
            ],
            "context": final_state["rag_context"][0].get("text", "") if final_state["rag_context"] else "Pas de contexte historique trouvé.",
            "opening": final_state["rag_context"][0].get("opening", "Ouverture inconnue") if final_state["rag_context"] else "N/A",
            "videos": final_state["videos"][:2],  # Top 2 vidéos
            "analysis_complete": final_state["analysis_complete"]
        }

        print(f"\n{'='*50}")
        print(f"✅ ANALYSE COMPLÈTE\n")
        print(json.dumps(response, indent=2, ensure_ascii=False))
        print(f"{'='*50}\n")

        return response

# ==========================================
# 5. INSTANCE GLOBALE
# ==========================================

chess_agent = ChessAgentService()
