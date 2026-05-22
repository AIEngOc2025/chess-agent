import chess
import requests
from stockfish import Stockfish

class ChessService:
    def __init__(self):
        try:
            self.stockfish = Stockfish()
        except:
            self.stockfish = None

    def get_theoretical_moves(self, fen: str):
        """Interroge l'API Lichess Explorer pour trouver les coups théoriques."""
        try:
            url = f"https://explorer.lichess.ovh/masters?fen={fen}"
            response = requests.get(url, timeout=5)

            if response.status_code == 200:
                data = response.json()
                moves = [
                    {
                        "uci": move['uci'],
                        "san": move.get('san', ''),
                        "white_wins": move.get('white', 0),
                        "draws": move.get('draws', 0),
                        "black_wins": move.get('black', 0)
                    }
                    for move in data.get('moves', [])[:5]  # Top 5 moves
                ]
                return {"source": "Lichess Opening Explorer", "moves": moves, "success": True}
            return {"source": "Lichess", "error": "Impossible de joindre l'API Lichess", "moves": [], "success": False}
        except Exception as e:
            return {"source": "Lichess", "error": str(e), "moves": [], "success": False}

    def evaluate_position_stockfish(self, fen: str, depth: int = 18) -> dict:
        """Évalue la position via Stockfish (analyse profonde)."""
        if not self.stockfish:
            return {"error": "Stockfish non disponible", "evaluation": 0}

        try:
            self.stockfish.set_fen_position(fen)
            evaluation = self.stockfish.get_evaluation()
            best_move = self.stockfish.get_best_move()

            if evaluation['type'] == 'mate':
                score = f"#M{evaluation['value']}"
            else:
                score = evaluation['value'] / 100.0

            return {
                "evaluation": score,
                "best_move": best_move,
                "depth": depth,
                "source": "Stockfish"
            }
        except Exception as e:
            return {"error": str(e), "source": "Stockfish"}

    @staticmethod
    def evaluate_position(fen: str):
        """Évaluation heuristique basée sur la valeur des pièces (fallback)."""
        try:
            board = chess.Board(fen)
            if not board.is_valid():
                return {"error": "Position FEN invalide"}

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

            legal_moves = list(board.legal_moves)
            best_move = legal_moves[0].uci() if legal_moves else "none"
            turn_str = "white" if board.turn == chess.WHITE else "black"

            return {
                "evaluation": f"{score / 100.0:+.2f}",
                "best_move": best_move,
                "turn": turn_str,
                "is_game_over": board.is_game_over()
            }
        except Exception as e:
            return {"error": str(e)}

chess_service = ChessService()
