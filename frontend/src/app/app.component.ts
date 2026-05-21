import { Component, AfterViewInit, ElementRef, ViewChild, ViewEncapsulation } from '@angular/core';
import { Chessground } from 'chessground';

@Component({
  selector: 'app-root',
  template: `
    <div style="text-align:center; font-family: Arial, sans-serif; margin-top: 20px;">
      <h1>♟️ FFE Chess Agent - Interface Angular 🤖</h1>
      <p>Échiquier propulsé par Chessground (Lichess Ecosystem)</p>
      
      <div style="display: flex; justify-content: center; gap: 40px; margin-top: 30px;">
        <div style="width: 400px; height: 400px; border: 2px solid #333; position: relative;">
          <div #chessgroundContainer class="cg-wrap brown cburnett" style="width: 100%; height: 100%;"></div>
        </div>
        
        <div style="width: 300px; text-align: left; background: #f5f5f5; padding: 15px; border-radius: 8px;">
          <h3>🤖 Recommandations de l'Agent</h3>
          <hr>
          <p><strong>Meilleur coup suggéré :</strong> En attente de l'API...</p>
          <p><strong>Contexte :</strong> Prêt pour l'analyse</p>
        </div>
      </div>
    </div>
  `,
  // Désactive l'encapsulation pour appliquer les styles globaux de Chessground aux éléments dynamiques
  encapsulation: ViewEncapsulation.None 
})
export class AppComponent implements AfterViewInit {
  @ViewChild('chessgroundContainer') container!: ElementRef;

  ngAfterViewInit() {
    Chessground(this.container.nativeElement, {
      orientation: 'white',
      coordinates: true,
      turnColor: 'white',
      movable: {
        color: 'white',
        free: true // Permet de tester en glissant les pièces librement
      }
    });
  }
}
