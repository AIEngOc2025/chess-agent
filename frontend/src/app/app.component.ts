import { Component, AfterViewInit, ElementRef, ViewChild, ViewEncapsulation } from '@angular/core';
import { Chessground } from 'chessground';
import { Api } from 'chessground/api';
import { ChessService, MoveRecommendation } from './services/chess.service';

@Component({
  selector: 'app-root',
  template: `
    <div style="text-align:center; font-family: Arial, sans-serif; margin-top: 20px;">
      <h1>♟️ FFE Chess Agent - Interface Angular 🤖</h1>
      <p>Échiquier propulsé par Chessground (Lichess Ecosystem)</p>
      
      <div style="display: flex; justify-content: center; gap: 40px; margin-top: 30px;">
        <div style="width: 450px; height: 450px; border: 2px solid #333; position: relative;">
          <div #chessgroundContainer class="cg-wrap brown cburnett" style="width: 100%; height: 100%;"></div>
        </div>
        
        <div style="width: 350px; text-align: left; background: #f8f9fa; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); display: flex; flex-direction: column; justify-content: space-between;">
          <div>
            <h3 style="margin-top: 0; display: flex; align-items: center; gap: 10px;">
              <span>🤖</span> Recommandations de l'Agent
            </h3>
            <hr style="border: 0; border-top: 1px solid #dee2e6; margin-bottom: 20px;">
            
            <div style="margin-bottom: 15px;">
              <span style="color: #6c757d; font-size: 0.9rem; display: block;">MEILLEUR COUP SUGGÉRÉ</span>
              <strong style="font-size: 1.4rem; color: #2b8a3e;">{{ agentData.best_move }}</strong>
            </div>

            <div style="margin-bottom: 15px;">
              <span style="color: #6c757d; font-size: 0.9rem; display: block;">ÉVALUATION DE LA POSITION</span>
              <span style="font-weight: bold; font-size: 1.1rem;" [style.color]="agentData.evaluation >= 0 ? '#2b8a3e' : '#c92a2a'">
                {{ agentData.evaluation > 0 ? '+' : '' }}{{ agentData.evaluation }}
              </span>
            </div>

            <div style="margin-bottom: 15px;">
              <span style="color: #6c757d; font-size: 0.9rem; display: block;">PROFONDEUR DE CALCUL</span>
              <span style="font-weight: bold;">{{ agentData.depth }} demi-coups (ply)</span>
            </div>

            <div style="margin-bottom: 15px;">
              <span style="color: #6c757d; font-size: 0.9rem; display: block;">CONTEXTE STRATÉGIQUE</span>
              <p style="margin: 5px 0 0 0; font-style: italic; background: #fff; padding: 10px; border-radius: 6px; border-left: 4px solid #1c7ed6; font-size: 0.95rem;">
                {{ agentData.context }}
              </p>
            </div>
          </div>

          <div style="margin-top: 20px;">
            <button (click)="resetBoard()" style="width: 100%; padding: 10px; background: #343a40; color: #fff; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 0.95rem; transition: background 0.2s;">
              🔄 Réinitialiser la partie
            </button>
          </div>
        </div>
      </div>
    </div>
  `,
  encapsulation: ViewEncapsulation.None 
})
export class AppComponent implements AfterViewInit {
  @ViewChild('chessgroundContainer') container!: ElementRef;
  
  private cgApi!: Api;
  
  // Valeurs par défaut stabilisées pour l'affichage initial
  public agentData: MoveRecommendation = {
    best_move: 'En attente du premier coup...',
    evaluation: 0.0,
    context: 'Début de partie. Faites glisser une pièce blanche pour initier l\'analyse de l\'Agent.',
    depth: 0
  };

  constructor(private chessService: ChessService) {}

  ngAfterViewInit() {
    this.cgApi = Chessground(this.container.nativeElement, {
      orientation: 'white',
      coordinates: true,
      turnColor: 'white',
      movable: {
        color: 'white',
        free: false, // On passe à false pour respecter les règles d'échecs standard (géré par les événements)
        dests: this.getInitialDests() // Liste des coups initiaux légaux de départ
      },
      events: {
        // Déclenché à chaque fois qu'une pièce est déplacée sur l'échiquier
        move: (orig, dest, captured) => {
          this.handleUserMove(orig, dest);
        }
      }
    });
  }

  /**
   * Intercepte le coup de l'utilisateur et l'envoie au service
   */
  private handleUserMove(orig: string, dest: string) {
    const uciMove = `${orig}${dest}`;
    this.agentData.best_move = 'Calcul en cours...';
    this.agentData.context = `L'agent analyse le coup joué : ${uciMove}...`;

    // 🚀 Envoi du coup UCI à ton API FastAPI via le service Angular
    this.chessService.sendMove(uciMove).subscribe({
      next: (response: MoveRecommendation) => {
        // Mise à jour dynamique du panneau avec la réponse de ton IA
        this.agentData = response;
        
        // Optionnel : Mettre à jour l'échiquier avec la réponse de l'agent si nécessaire
        this.cgApi.set({ turnColor: 'white' });
      },
      error: (err) => {
        console.error('Erreur API Backend:', err);
        this.agentData.best_move = 'Erreur';
        this.agentData.context = 'Impossible de joindre l\'API FastAPI. Vérifie que le serveur backend tourne sur le port 8000.';
      }
    });
  }

  /**
   * Réinitialise l'échiquier à la position initiale
   */
  public resetBoard() {
    this.cgApi.set({
      fen: 'start',
      turnColor: 'white'
    });
    this.agentData = {
      best_move: 'En attente du premier coup...',
      evaluation: 0.0,
      context: 'Partie réinitialisée. En attente de l\'analyse.',
      depth: 0
    };
  }

  /**
   * Génère les destinations légales de base pour le premier coup (standard échecs)
   */
  private getInitialDests() {
    const dests = new Map();
    // Liste simplifiée des premiers coups possibles pour les pions et cavaliers blancs
    const files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'];
    files.forEach(f => {
      dests.set(`${f}2`, [`${f}3`, `${f}4`]);
    });
    dests.set('b1', ['a3', 'c3']);
    dests.set('g1', ['f3', 'h3']);
    return dests;
  }
}
