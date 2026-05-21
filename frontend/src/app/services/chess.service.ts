import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface MoveRecommendation {
  best_move: string;      // ex: "e2e4"
  evaluation: number;     // Score ex: +0.4
  context: string;        // Commentaire textuel de l'agent
  depth: number;          // Profondeur de calcul de l'IA
}

@Injectable({
  providedIn: 'root'
})
export class ChessService {
  // Ajuste l'URL selon la configuration réseau de ton docker-compose pour FastAPI
  private apiUrl = 'http://localhost:8000/api/v1/chess';

  constructor(private http: HttpClient) {}

  /**
   * Envoie la position actuelle (ou le coup) à l'Agent IA pour analyse
   * @param fen Chaîne FEN représentant la position sur l'échiquier
   */
  getRecommendation(fen: string): Observable<MoveRecommendation> {
    return this.http.post<MoveRecommendation>(`${this.apiUrl}/analyze`, { fen });
  }

  /**
   * Envoie un coup au format UCI (ex: "e2e4") au backend
   */
  sendMove(moveUci: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/move`, { move: moveUci });
  }
}
