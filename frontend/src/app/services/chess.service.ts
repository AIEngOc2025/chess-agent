import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface MoveRecommendation {
  move_requested: string;
  best_move: string;
  evaluation: number | string;
  depth: number;
  theoretical_moves: string[];
  context: string;
  opening: string;
  videos: any[];
  analysis_complete: boolean;
}

@Injectable({
  providedIn: 'root'
})
export class ChessService {
  private apiUrl = 'http://localhost:8000/api/v1';

  constructor(private http: HttpClient) {}

  /**
   * Envoie un coup (UCI) + position FEN pour analyse complète
   */
  sendMove(moveUci: string, fen: string = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"): Observable<MoveRecommendation> {
    return this.http.post<MoveRecommendation>(`${this.apiUrl}/chess/move`, {
      move: moveUci,
      fen: fen
    });
  }

  /**
   * Recherche vectorielle dans la base de connaissances Milvus
   */
  searchKnowledge(query: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/vector-search`, { query });
  }

  /**
   * Récupère des vidéos éducatives pour une ouverture
   */
  getVideos(opening: string): Observable<any> {
    return this.http.get(`${this.apiUrl}/videos/${opening}`);
  }

  /**
   * Vérifie la santé de l'API
   */
  healthCheck(): Observable<any> {
    return this.http.get(`${this.apiUrl}/healthcheck`);
  }
}
