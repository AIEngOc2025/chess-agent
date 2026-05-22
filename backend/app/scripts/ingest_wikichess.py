import os
import time
# pyrefly: ignore [missing-import]
from pymilvus import (
    connections,
    utility,
    FieldSchema,
    CollectionSchema,
    DataType,
    Collection
)

# On utilise sentence-transformers pour générer des embeddings locaux de qualité
# pyrefly: ignore [missing-import]
from sentence_transformers import SentenceTransformer

# ==========================================
# 1. CONFIGURATION & CONSTANTES
# ==========================================
MILVUS_HOST = os.getenv("MILVUS_HOST", "localhost")
MILVUS_PORT = os.getenv("MILVUS_PORT", "19530")
COLLECTION_NAME = "wikichess_knowledge"
DIMENSION = 384  # Dimension pour le modèle 'all-MiniLM-L6-v2'

# Exemple de base de connaissances WikiChess à ingérer
WIKICHESS_DATA = [
    {
        "title": "Défense Sicilienne",
        "text": "La défense sicilienne est une ouverture d'échecs caractérisée par les coups 1.e4 c5. C'est la réponse la plus populaire et la plus dynamique contre 1.e4, luttant immédiatement pour le contrôle de la case d4 depuis l'aile dame."
    },
    {
        "title": "Gambit Dame Refusé",
        "text": "Le Gambit Dame Refusé commence par 1.d4 d5 2.c4 e6. Les noirs choisissent de solidifier leur pion central en d5 plutôt que de capturer le pion de sacrifice en c4, menant à un jeu stratégique, fermé et solide."
    },
    {
        "title": "Attaque de minorité",
        "text": "L'attaque de minorité est un plan stratégique à long terme sur l'aile dame, typique des structures de pions Carlsbad. Le camp qui possède le moins de pions avance sa minorité pour créer des faiblesses structurelles chez l'adversaire."
    },
    {
        "title": "Structure Carlsbad",
        "text": "La structure Carlsbad apparaît fréquemment dans le Gambit Dame Refusé. Elle est définie par une chaîne de pions blancs asymétrique et demande souvent une attaque de minorité ou une expansion centrale à base de e3-e4."
    }
]


# ==========================================
# 2. FONCTION PRINCIPALE D'INGESTION
# ==========================================
def main():
    print("🤖 [INGEST] Initialisation du modèle d'embeddings sémantiques...")
    # Initialisation du modèle d'embedding (léger, rapide et performant)
    model = SentenceTransformer("all-MiniLM-L6-v2")

    print(f"🔌 [INGEST] Connexion au serveur Milvus ({MILVUS_HOST}:{MILVUS_PORT})...")
    connections.connect("default", host=MILVUS_HOST, port=MILVUS_PORT)

    # Nettoyage : si la collection existe déjà, on la supprime pour éviter les doublons
    if utility.has_collection(COLLECTION_NAME):
        print(f"🗑️ [INGEST] Suppression de l'ancienne collection '{COLLECTION_NAME}'...")
        utility.drop_collection(COLLECTION_NAME)

    # Définition du schéma de la table/collection dans Milvus
    print("📐 [INGEST] Définition du schéma de la collection...")
    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=200),
        FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=2000),
        FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dimension=DIMENSION)
    ]
    schema = CollectionSchema(fields, description="Base de connaissances WikiChess pour agent RAG")
    collection = Collection(COLLECTION_NAME, schema)

    # Préparation des listes de données pour l'insertion par colonnes (standard Milvus)
    titles = []
    texts = []
    raw_sentences = []

    for item in WIKICHESS_DATA:
        titles.append(item["title"])
        texts.append(item["text"])
        # On encode le titre combiné au texte pour maximiser la pertinence sémantique
        raw_sentences.append(f"{item['title']} : {item['text']}")

    print("🧠 [INGEST] Génération des embeddings vectoriels...")
    embeddings = model.encode(raw_sentences, convert_to_numpy=True).tolist()

    # Insertion des données
    print(f"📥 [INGEST] Insertion de {len(WIKICHESS_DATA)} documents dans Milvus...")
    data_to_insert = [titles, texts, embeddings]
    collection.insert(data_to_insert)

    # Flush pour s'assurer que les données soient bien écrites sur le disque
    collection.flush()
    print(f"✅ [INGEST] Nombre d'entités insérées : {collection.num_entities}")

    # Création de l'index de recherche (essentiel pour pouvoir exécuter des requêtes de similarité)
    print("⚡ [INGEST] Création de l'index de recherche IVF_FLAT...")
    index_params = {
        "metric_type": "COSINE",  # On mesure la proximité par similarité cosinus
        "index_type": "IVF_FLAT",
        "params": {"nlist": 128}
    }
    collection.create_index(field_name="vector", index_params=index_params)
    
    print("🎉 [INGEST] Ingestion WikiChess terminée avec succès ! La collection est prête.")


if __name__ == "__main__":
    start_time = time.time()
    main()
    print(f"⏱️ Temps total d'exécution : {round(time.time() - start_time, 2)} secondes")