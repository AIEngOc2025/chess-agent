import { Component, AfterViewInit, ElementRef, ViewChild, ViewEncapsulation } from '@angular/core';
import { Chessground } from 'chessground';
import { Api } from 'chessground/api';
import { Chess } from 'chess.js';
import { ChessService, MoveRecommendation } from './services/chess.service';

@Component({
  selector: 'app-root',
  template: `
    <div style="text-align:center; font-family: Arial, sans-serif; margin-top: 20px;">
      <h1>♟️ FFE Chess Agent - Interface Angular 🤖</h1>
      <p style="color: #666;">Agent IA pour l'apprentissage des échecs - Powered by LangGraph & Stockfish</p>

      <div style="display: flex; justify-content: center; gap: 40px; margin-top: 30px;">
        <!-- ÉCHIQUIER -->
        <div style="width: 450px; height: 450px; border: 2px solid #333; position: relative;">
          <div #chessgroundContainer class="cg-wrap brown cburnett" style="width: 100%; height: 100%;"></div>
        </div>

        <!-- PANNEAU RECOMMANDATIONS -->
        <div style="width: 350px; text-align: left; background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); padding: 20px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); display: flex; flex-direction: column; gap: 15px;">

          <!-- En-tête -->
          <div>
            <h3 style="margin-top: 0; display: flex; align-items: center; gap: 10px; color: #2c3e50;">
              <span>🤖</span> Recommandations IA
            </h3>
            <hr style="border: 0; border-top: 2px solid #dee2e6; margin: 0;">
          </div>

          <!-- Meilleur coup -->
          <div style="background: #fff; padding: 12px; border-radius: 8px; border-left: 4px solid #2b8a3e;">
            <span style="color: #6c757d; font-size: 0.85rem; display: block; font-weight: 600;">🎯 MEILLEUR COUP</span>
            <div style="font-size: 1.6rem; color: #2b8a3e; font-weight: bold; margin-top: 5px;">
              {{ agentData.best_move !== 'N/A' ? agentData.best_move : '...' }}
            </div>
          </div>

          <!-- Évaluation -->
          <div style="background: #fff; padding: 12px; border-radius: 8px; border-left: 4px solid #1c7ed6;">
            <span style="color: #6c757d; font-size: 0.85rem; display: block; font-weight: 600;">⚖️ ÉVALUATION</span>
            <div style="margin-top: 5px;">
              <span style="font-weight: bold; font-size: 1.3rem;" [style.color]="getEvalColor()">
                {{ formatEvaluation(agentData.evaluation) }}
              </span>
              <span style="color: #6c757d; font-size: 0.8rem; margin-left: 10px;">Profondeur: {{ agentData.depth }}</span>
            </div>
          </div>

          <!-- Ouverture -->
          <div style="background: #fff; padding: 12px; border-radius: 8px; border-left: 4px solid #fd7e14;">
            <span style="color: #6c757d; font-size: 0.85rem; display: block; font-weight: 600;">📚 OUVERTURE</span>
            <div style="font-size: 1rem; color: #2c3e50; font-weight: 500; margin-top: 5px;">
              {{ agentData.opening || 'Indéterminée' }}
            </div>
          </div>

          <!-- Contexte pédagogique -->
          <div style="background: #fff; padding: 12px; border-radius: 8px; border-left: 4px solid #7c3aed;">
            <span style="color: #6c757d; font-size: 0.85rem; display: block; font-weight: 600;">💡 CONTEXTE</span>
            <p style="margin: 8px 0 0 0; font-size: 0.9rem; color: #495057; line-height: 1.4;">
              {{ agentData.context || 'Analyse en cours...' }}
            </p>
          </div>

          <!-- Vidéos -->
          <div style="background: #fff; padding: 12px; border-radius: 8px;">
            <span style="color: #6c757d; font-size: 0.85rem; display: block; font-weight: 600;">🎬 VIDÉOS ÉDUCATIVES</span>
            <div style="margin-top: 8px; display: flex; flex-direction: column; gap: 8px;">
              <ng-container *ngIf="agentData.videos && agentData.videos.length > 0; else noVideos">
                <a *ngFor="let video of agentData.videos"
                   [href]="video.video_url"
                   target="_blank"
                   style="font-size: 0.9rem; color: #1c7ed6; text-decoration: none; cursor: pointer; padding: 6px; border-radius: 4px; background: #e7f5ff; transition: all 0.2s;">
                  📺 {{ video.title | slice:0:40 }}...
                </a>
              </ng-container>
              <ng-template #noVideos>
                <span style="font-size: 0.9rem; color: #6c757d; font-style: italic;">Pas de vidéos disponibles</span>
              </ng-template>
            </div>
          </div>

          <!-- Boutons d'action -->
          <div style="display: flex; gap: 10px; margin-top: 10px;">
            <button (click)="resetBoard()"
                    style="flex: 1; padding: 10px; background: #6c757d; color: #fff; border: none; border-radius: 6px; cursor: pointer; font-weight: 600; transition: background 0.2s;"
                    onmouseover="this.style.background='#5a6268'"
                    onmouseout="this.style.background='#6c757d'">
              🔄 Réinitialiser
            </button>
            <button (click)="showStats()"
                    style="flex: 1; padding: 10px; background: #17a2b8; color: #fff; border: none; border-radius: 6px; cursor: pointer; font-weight: 600; transition: background 0.2s;"
                    onmouseover="this.style.background='#138496'"
                    onmouseout="this.style.background='#17a2b8'">
              ℹ️ Infos
            </button>
          </div>

          <!-- Status -->
          <div style="font-size: 0.85rem; color: #6c757d; text-align: center;">
            <span *ngIf="!agentData.analysis_complete">⏳ Analyse en cours...</span>
            <span *ngIf="agentData.analysis_complete">✅ Analyse complète</span>
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
  private game!: Chess;

  public agentData: MoveRecommendation = {
    move_requested: '',
    best_move: 'Coup recommandé',
    evaluation: 0.0,
    depth: 0,
    theoretical_moves: [],
    context: 'Commencez par jouer un coup blanc...',
    opening: 'Position initiale',
    videos: [],
    analysis_complete: false
  };

  constructor(private chessService: ChessService) {
    this.game = new Chess();
  }

  ngAfterViewInit() {
    this.cgApi = Chessground(this.container.nativeElement, {
      orientation: 'white',
      coordinates: true,
      turnColor: 'white',
      movable: {
        color: 'white',
        free: false,
        dests: this.getLegalMoves()
      },
      events: {
        move: (orig, dest) => this.handleUserMove(orig, dest)
      }
    });

    // Vérification de la santé de l'API
    this.chessService.healthCheck().subscribe(
      (health) => console.log('✅ API backend connectée', health),
      (err) => console.error('❌ Erreur connexion backend', err)
    );
  }

  private handleUserMove(orig: string, dest: string) {
    const moveObj = this.game.moves({ square: orig as any, verbose: true }).find(
      m => m.from === orig && m.to === dest
    );

    if (!moveObj) return;

    this.game.move(moveObj);
    const uciMove = `${orig}${dest}`;
    const currentFen = this.game.fen();

    this.agentData.best_move = '⏳ Calcul...';
    this.agentData.context = `Analyse du coup: ${uciMove}`;
    this.agentData.analysis_complete = false;

    this.chessService.sendMove(uciMove, currentFen).subscribe({
      next: (response) => {
        this.agentData = response;
        this.updateBoard();
      },
      error: (err) => {
        console.error('❌ Erreur API:', err);
        this.agentData.best_move = 'Erreur';
        this.agentData.context = 'Impossible de joindre le backend.';
      }
    });
  }

  private updateBoard() {
    this.cgApi.set({
      fen: this.game.fen(),
      movable: {
        color: this.game.turn() === 'w' ? 'white' : 'black',
        free: false,
        dests: this.getLegalMoves()
      }
    });
  }

  private getLegalMoves(): Map<string, string[]> {
    const dests = new Map();
    this.game.moves({ verbose: true }).forEach(move => {
      if (!dests.has(move.from)) {
        dests.set(move.from, []);
      }
      dests.get(move.from)!.push(move.to);
    });
    return dests;
  }

  public resetBoard() {
    this.game.reset();
    this.cgApi.set({
      fen: this.game.fen(),
      turnColor: 'white',
      movable: {
        color: 'white',
        free: false,
        dests: this.getLegalMoves()
      }
    });
    this.agentData = {
      move_requested: '',
      best_move: 'Coup recommandé',
      evaluation: 0.0,
      depth: 0,
      theoretical_moves: [],
      context: 'Position réinitialisée. À vous de jouer !',
      opening: 'Position initiale',
      videos: [],
      analysis_complete: false
    };
  }

  public showStats() {
    alert('Coup demandé: ' + this.agentData.move_requested + '\n' +
          'FEN: ' + this.game.fen());
  }

  public formatEvaluation(value: any): string {
    if (typeof value === 'string') return value;
    if (typeof value === 'number') {
      return (value >= 0 ? '+' : '') + value.toFixed(2);
    }
    return '0.00';
  }

  public getEvalColor(): string {
    const val = typeof this.agentData.evaluation === 'number' ? this.agentData.evaluation : 0;
    if (val > 0.5) return '#2b8a3e';
    if (val < -0.5) return '#c92a2a';
    return '#6c757d';
  }
}
