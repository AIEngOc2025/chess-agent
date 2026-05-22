# MISSION : Développez un agent IA pour l'apprentissage des échecs (FFE)

## 📋 Contexte du Projet
La **Fédération Française des Échecs (FFE)** souhaite, en vue des futurs championnats d'Europe jeunes, proposer un **agent intelligent** capable d'accompagner les jeunes espoirs dans l'apprentissage des ouvertures aux échecs[cite: 361, 362]. 


En tant qu'**IA Engineer junior**, vous êtes missionné pour développer un **POC (Proof of Concept)** fonctionnel de cet agent en **2 semaines**.

---

## 🎯 Objectifs & Fonctionnalités du POC
L'agent IA doit guider les utilisateurs à travers une interface web en leur apportant plusieurs niveaux d'assistance et d'analyse:

1. **Théorie des ouvertures** : Proposer les meilleurs coups issus de la théorie.
2. **Enrichissement Historique** : Donner le contexte des ouvertures grâce à des données enrichies par des parties historiques.
3. **Ressources Pédagogiques** : Afficher des vidéos explicatives YouTube pertinentes par rapport à la situation de jeu.
4. **Analyse de Secours (Stockfish)** : Évaluer la position via un moteur spécialisé si la partie s'écarte des sentiers battus de la théorie.

---

## 🛠️ Stack Technique Imposée
Le système complet doit être orchestré et architecturé avec les technologies suivantes:
* **Frontend** : Angular (avec la bibliothèque d'échiquier interactif `ngx-chessboard`).
* **Backend API** : FastAPI.
* **Orchestration IA** : LangGraph.
* **Bases de données** : 
  * Milvus (Base de données vectorielle pour le RAG sur Wikichess).
  * MongoDB (Base de données documentaire pour la persistance des données).
* **Conteneurisation** : Docker Compose (pour une exécution locale).

---

## 🚀 Étapes de Réalisation du Projet

### Étape 1 - Préparation de l'environnement de développement
* Initialisation du dépôt Git pour le code source.
* Configuration et lancement des conteneurs requis (Milvus, MongoDB) via Docker Compose.

### Étape 2 - Développement de l'agent backend (FastAPI & LangGraph)
* Implémentation des points de terminaison (endpoints) principaux:
  * `GET /api/v1/moves/{fen}` : Retourne les coups théoriques possibles depuis l'API Lichess.
  * `GET /api/v1/evaluate/{fen}` : Retourne l'évaluation de la position en *centipawns* via Stockfish.
* Recommandations : Utiliser `python-chess` pour valider la légalité des coups et encapsuler la logique dans un module `service` dédié.
* Points de vigilance : Gérer les timeouts et respecter les quotas/limites de requêtes de l'API Lichess.

### Étape 3 - Intégration de la connaissance (RAG avec Milvus)
* Extraction d'un jeu de données textuelles (5 à 10 articles) depuis Wikichess concernant les ouvertures populaires (Sicilienne, Italienne, Espagnole...).
* Création d'un script d'ingestion pour transformer ces textes en vecteurs à l'aide d'un modèle léger (ex: `qwen3B-embedding-0.6B`) et les indexer dans Milvus.
* Implémentation de l'endpoint `POST /vector-search` pour interroger cette base vectorielle.

### Étape 4 - Intégration de l'API YouTube
* Implémentation de l'endpoint `GET /api/v1/videos/{opening}` à l'aide de la bibliothèque `google-api-python-client`.
* Construction de requêtes de recherche intelligentes combinant le nom de l'ouverture et des mots-clés (`chess opening`, `tutorial`, `explanation`).
* Points de vigilance : Gestion stricte des quotas d'API YouTube et filtrage qualitatif des vidéos.

### Étape 5 - Développement de l'interface Angular
* Intégration de l'échiquier dynamique interactif à l'aide de `ngx-chessboard`.
* Création d'un panneau latéral complet affichant les recommandations fournies en temps réel par l'agent IA (coups suggérés, contexte historique issu du RAG, vidéos YouTube correspondantes).
* Liaison et communication asynchrone avec les services de l'API FastAPI backend.

### Étape 6 - Packaging et conteneurisation
* Écriture et finalisation du fichier `docker-compose.yml` unifiant tous les services applicatifs (Frontend, Backend, Bases de données).
* Rédaction d'une documentation claire et exhaustive (`README.md`) décrivant la procédure d'installation et de démarrage rapide.

---
## 🧠 Partie Stratégique : Étude de Faisabilité (Analyse Vidéo)
En parallèle du développement du POC, votre responsable Alan vous demande de concevoir et documenter (sans l'implémenter) un **système avancé d'analyse vidéo** basé sur le **Model Context Protocol (MCP)**.

### Problématique ciblée
Les requêtes textuelles simples sur YouTube renvoient souvent des vidéos trop longues (ex: 45 minutes) qui ne ciblent pas le coup précis joué par l'utilisateur.

### Solution à concevoir
Un système capable de :
1. Stocker des vidéos d'échecs pertinentes.
2. Analyser chaque vidéo pour en extraire les images (*frames*).
3. Détecter la présence d'un échiquier sur chaque frame et convertir la position de jeu en notation **FEN** à l'aide d'un modèle de vision spécialisé (*board-to-FEN*).
4. Renvoyer à l'utilisateur le lien exact de la vidéo accompagné d'un **timestamp précis** correspondant à sa position actuelle sur l'échiquier.
5. Porter ce système via un serveur MCP pour qu'il s'interface nativement avec l'application principale.

### Livrables attendus pour l'étude
Une note technique détaillée d'environ **8 à 10 pages** comprenant:
* Les bénéfices attendus et les limites techniques intrinsèques de ce système.
* Un schéma d'architecture technique détaillé de la solution utilisant MCP (avec FastMCP).
* Une étude de faisabilité financière complète (estimations des coûts de build + coûts d'exploitation OPEX : stockage, calcul computationnel, appels API).

---

## 📦 Livrables Finaux à Fournir
* **Le système complet fonctionnel** : Code source complet orchestré via FastAPI, LangGraph, Milvus et MongoDB.
* **Le dépôt Git** accessible avec l'historique de commit.
* **L'interface Angular** connectée et utilisable en local.
* **Le fichier Docker Compose** opérationnel pour la démonstration client.
* **La note d'étude de faisabilité MCP** (8-10 pages) pour le système d'analyse vidéo par vision artificielle.