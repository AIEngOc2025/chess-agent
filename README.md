# ♟️ FFE Chess Agent - Agent IA pour l'Apprentissage des Échecs

Agent intelligent propulsé par **LangGraph**, **FastAPI**, **Milvus** et **Angular** pour accompagner les jeunes espoirs de la **Fédération Française des Échecs (FFE)** dans l'apprentissage des ouvertures.

---

## 🎯 Objectifs

L'agent fournit **4 niveaux d'assistance pédagogique**:

1. **Théorie des ouvertures** - Coups théoriques via Lichess Explorer API
2. **Enrichissement historique** - Contexte pédagogique issu d'une base vectorielle Milvus
3. **Analyse de position** - Évaluation Stockfish du meilleur coup
4. **Ressources éducatives** - Vidéos YouTube recommandées par ouverture

---

## 🛠️ Stack Technique

| Composant | Technologie | Rôle |
|-----------|------------|------|
| **Backend** | FastAPI + LangGraph | API REST + orchestration IA |
| **Frontend** | Angular 17 | Interface web interactive |
| **Échiquier** | Chessground | Visualisation et saisie des coups |
| **Moteur d'échecs** | Stockfish | Évaluation profonde des positions |
| **Base vectorielle** | Milvus | RAG (Retrieval-Augmented Generation) |
| **Persistance** | MongoDB | Stockage des parties et contexte |
| **Conteneurisation** | Docker Compose | Orchestration locale |

---

## 📋 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND (Angular 17)                    │
│                  Chessground + Chess.js                      │
│               Interface pour joueur humain                   │
└─────────────────────────────────────────────────────────────┘
                            ↓ (HTTP/REST)
┌─────────────────────────────────────────────────────────────┐
│                  BACKEND (FastAPI + LangGraph)               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         Orchestration Workflow (LangGraph)           │   │
│  │                                                       │   │
│  │  Move → Théorie → Évaluation → RAG → Vidéos → Réponse │  │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
         ↓              ↓              ↓              ↓
    [Lichess API]  [Stockfish]  [Milvus RAG]  [YouTube API]
```

---

## 🚀 Démarrage Rapide

### Prérequis

- **Docker** et **Docker Compose** 
- **Python 3.11+** (pour développement local)
- **Node.js 18+** (pour le frontend)

### 1️⃣ Installation

```bash
# Cloner le repository
git clone <votre-repo>
cd chess-agent

# Créer l'environnement virtuel Python (optionnel pour docker)
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# ou
.venv\Scripts\activate  # Windows
```

### 2️⃣ Configuration

Vérifiez le fichier `.env` :

```bash
# .env
MONGO_URI=mongodb://admin:secret@chess_mongodb:27017
MILVUS_HOST=milvus-standalone
MILVUS_PORT=19530
YOUTUBE_API_KEY=  # Optionnel - fonctionne en mode démo sans clé
STOCKFISH_DEPTH=18
```

### 3️⃣ Lancer le Stack Complet

```bash
# Démarrer tous les services (Milvus, MongoDB, Backend, Frontend)
docker-compose up -d

# Attendre ~30s pour l'initialisation des services
sleep 30

# Vérifier que tout fonctionne
curl http://localhost:8000/api/v1/healthcheck
```

### 4️⃣ Accès à l'Interface

- **Frontend Angular**: http://localhost:4200
- **API FastAPI Docs**: http://localhost:8000/docs
- **Milvus Dashboard** (optionnel): http://localhost:8001

---

## 📡 Endpoints API

### Health & Debug

```bash
# Vérifier la santé de l'API
GET /api/v1/healthcheck

# Statistiques et features
GET /api/v1/stats
```

### Chess Analysis (Orchestration Principale)

```bash
# Analyser un coup avec position FEN
POST /api/v1/chess/move
{
  "move": "e2e4",
  "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
}

# Réponse:
{
  "move_requested": "e2e4",
  "best_move": "e7e5",
  "evaluation": 0.25,
  "depth": 18,
  "theoretical_moves": ["e7e5", "c7c5", "d7d5"],
  "context": "L'ouverture italienne crée une asymétrie...",
  "opening": "Partie Italienne",
  "videos": [
    {
      "title": "Italian Game Tutorial",
      "video_url": "https://youtube.com/watch?v=..."
    }
  ],
  "analysis_complete": true
}
```

### Recherche Vectorielle (RAG)

```bash
# Rechercher dans la base de connaissances
POST /api/v1/vector-search
{
  "query": "sicilienne defense"
}

# Réponse:
{
  "query": "sicilienne defense",
  "results": [
    {
      "opening": "Défense Sicilienne",
      "text": "La défense sicilienne (1.e4 c5)...",
      "distance": 0.15
    }
  ]
}
```

### Ressources Éducatives

```bash
# Récupérer des vidéos sur une ouverture
GET /api/v1/videos/{opening_name}

# Exemple:
GET /api/v1/videos/Italian Game

# Réponse:
{
  "opening": "Italian Game",
  "videos": [
    {
      "title": "Italian Game Tutorial",
      "video_url": "https://youtube.com/watch?v=...",
      "channel_name": "Chess Channel",
      "thumbnail_url": "..."
    }
  ],
  "count": 2
}
```

---

## 🧠 Architecture du Workflow LangGraph

```python
# Chaque analyse suit ce pipeline:

1. EXTRACT_MOVE
   └─→ Valider le coup UCI

2. (Parallèle)
   ├─→ FETCH_THEORETICAL_MOVES (Lichess API)
   ├─→ EVALUATE_POSITION (Stockfish)
   └─→ SEARCH_KNOWLEDGE_BASE (Milvus RAG)
           └─→ FIND_VIDEOS (YouTube API)

3. COMPILE_ANALYSIS
   └─→ Synthèse complète
```

**Temps d'exécution**: ~1-2s (selon la charge Stockfish)

---

## 🗂️ Structure du Projet

```
chess-agent/
├── backend/
│   ├── app/
│   │   ├── main.py                 # API FastAPI
│   │   ├── core/
│   │   │   └── database.py         # Connexions MongoDB/Milvus
│   │   └── services/
│   │       ├── chess_agent.py      # LangGraph Orchestration
│   │       ├── chess_service.py    # Lichess + Stockfish
│   │       ├── rag_service.py      # Milvus RAG
│   │       └── youtube_service.py  # YouTube API
│   ├── requirements.txt             # Dépendances Python
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── app.component.ts    # Composant principal
│   │   │   ├── app.module.ts       # Module Angular
│   │   │   └── services/
│   │   │       └── chess.service.ts # Service HTTP
│   │   └── main.ts
│   ├── package.json
│   └── Dockerfile
│
├── docker-compose.yml              # Orchestration (Milvus, MongoDB, Services)
├── .env                            # Variables d'environnement
└── README.md
```

---

## 🔧 Développement Local (sans Docker)

### Backend

```bash
cd backend
pip install -r requirements.txt

# Lancer l'API (Milvus/MongoDB doivent tourner)
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm start  # Démarre ng serve sur http://localhost:4200
```

---

## 📊 Données de Démo (RAG)

3 ouvertures sont pré-chargées dans Milvus :

1. **Défense Sicilienne** (1.e4 c5)
2. **Partie Italienne** (1.e4 e5 2.Nf3 Nc6 3.Bc4)
3. **Partie Espagnole** (1.e4 e5 2.Nf3 Nc6 3.Bb5)

Pour ajouter plus de données, éditez `app/services/rag_service.py` dans la méthode `init_db()`.

---

## 🎬 Intégration YouTube

Par défaut, l'API fonctionne en **mode démo** sans clé YouTube.

Pour activer les vraies vidéos :

1. Créez une clé API sur [Google Cloud Console](https://console.cloud.google.com)
2. Exportez dans `.env` : `YOUTUBE_API_KEY=votre_clé`
3. Redémarrez les services

**Note**: Chaque requête consomme ~100 quotas. Prudence en production !

---

## ⚙️ Configuration Avancée

### Stockfish (Profondeur d'analyse)

```bash
# Dans .env
STOCKFISH_DEPTH=18  # Par défaut (rapide)
STOCKFISH_DEPTH=24  # Pour analyse plus profonde (plus lent)
```

### Milvus (Optimisation RAG)

```python
# Dans app/services/rag_service.py
search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
limit=1  # Nombre de résultats à retourner
```

---

## 🧪 Tests

```bash
# Tester la santé de l'API
curl http://localhost:8000/api/v1/healthcheck | jq

# Tester une analyse complète
curl -X POST http://localhost:8000/api/v1/chess/move \
  -H "Content-Type: application/json" \
  -d '{"move": "e2e4", "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"}' | jq
```

---

## 🐛 Troubleshooting

### "Impossible de joindre l'API FastAPI"

```bash
# Vérifier que le backend tourne
docker-compose ps

# Logs du backend
docker-compose logs chess_backend

# Vérifier le port 8000
curl http://localhost:8000/api/v1/healthcheck
```

### "Erreur Milvus"

```bash
# Vérifier que Milvus est connecté
docker-compose logs standalone

# Réinitialiser la base:
curl http://localhost:8000/api/v1/rag/init
```

### "npm dependencies not found"

```bash
cd frontend
npm install
npm start
```

---

## 📝 Notes Techniques

### LangGraph State Management

Chaque requête passe dans un **StateGraph TypedDict** :

```python
class AgentState(TypedDict):
    move: str                         # Coup UCI
    fen: str                          # Position FEN
    theoretical_moves: dict           # Résultats Lichess
    evaluation: dict                  # Résultats Stockfish
    rag_context: list                 # Documents Milvus
    videos: list                      # Résultats YouTube
    analysis_complete: bool           # Flag final
```

### Pipeline d'Exécution (Parallèle + Séquentiel)

```
extract → [theoretical || evaluate || rag] → compile → END
                          └─→ videos ─→
```

---

## 🚀 Déploiement en Production

Pour déployer en production :

1. **Dockerfile Backend**: Adapter la configuration Uvicorn
2. **Dockerfile Frontend**: Build Angular optimisé (`ng build --prod`)
3. **Kubernetes/Cloud**: Remplacer docker-compose par une orchestration scalable
4. **Secrets**: Utiliser un gestionnaire de secrets (AWS Secrets Manager, etc.)
5. **Monitoring**: Ajouter OpenTelemetry/Prometheus

---

## 📚 Références

- **LangGraph Docs**: https://langchain-ai.github.io/langgraph/
- **FastAPI**: https://fastapi.tiangolo.com/
- **Milvus**: https://milvus.io/docs
- **Chessground**: https://github.com/lichess-org/chessground
- **Stockfish**: https://stockfishchess.org/

---

## 📄 Livrable - Étude de Faisabilité MCP

Une note technique complète sur l'architecture d'un système d'analyse vidéo par vision artificielle est disponible :  
**Voir : `Note_Technique_MCP_FFE.docx`**

---

## 👨‍💻 Auteur

**Développé pour**: Fédération Française des Échecs (FFE)  
**Mission**: Agent IA pour l'apprentissage des ouvertures aux jeunes espoirs

---

## 📞 Support

En cas de problème :
1. Vérifiez les logs : `docker-compose logs -f`
2. Testez les endpoints : `curl http://localhost:8000/api/v1/healthcheck`
3. Consultez la structure : `docker-compose ps`

---

**Version**: 1.0.0  
**Dernière mise à jour**: Mai 2026  
**Status**: 🟢 Production-Ready
