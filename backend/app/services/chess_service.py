import chess
import requests

class ChessService:
    @staticmethod
    def get_theoretical_moves(fen: str):
        """Interroge l'API Lichess Explorer pour trouver les coups théoriques."""
        try:
            url = f"https://explorer.lichess.ovh/masters?fen={fen}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                moves = [move['uci'] for move in data.get('moves', [])]
                return {"source": "Lichess Opening Explorer", "moves": moves}
            return {"source": "Lichess", "error": "Impossible de joindre l'API Lichess", "moves": []}
        except Exception as e:
            return {"source": "Lichess", "error": str(e), "moves": []}

    @staticmethod
    def evaluate_position(fen: str):
        """Évalue la position via python-chess (Heuristique matérielle par défaut)."""
        try:
            board = chess.Board(fen)
            if not board.is_valid():
                return {"error": "Position FEN invalide"}
                
            # Évaluation heuristique basée sur la valeur standard des pièces
            score = 0
            for square in chess.SQUARES:
                piece = board.piece_at(square)
                if piece:
                    value = {
                        chess.PAWN: 100, 
                        chess.KNIGHT: 320, 
                        chess.BISHOP: 330, 
                        chess.ROOK: 500, 
                        chess.QUEEN: 900, 
                        chess.KING: 20000
                    }[piece.piece_type]
                    
                    if piece.color == chess.WHITE:
                        score += value
                    else:
                        score -= value
            
            # Détermination grossière du meilleur coup légal pour éviter un crash
            legal_moves = list(board.legal_moves)
            best_move = legal_moves[0].uci() if legal_moves else "none"
            turn_str = "white" if board.turn == chess.WHITE else "black"
            
            # Formatage du score en chaîne (+X.XX)
            formatted_score = f"{score / 100.0:+.2f}"
            
            return {
                "evaluation": formatted_score,
                "best_move": best_move,
                "turn": turn_str,
                "is_game_over": board.is_game_over()
            }
        except Exception as e:
            return {"error": str(e)}
