import os
from pymilvus import connections, utility, FieldSchema, CollectionSchema, DataType, Collection
from sentence_transformers import SentenceTransformer

class RAGService:
    def __init__(self):
        self.model_name = "all-MiniLM-L6-v2"  # Équivalent léger et stable recommandé
        self.model = SentenceTransformer(self.model_name)
        self.collection_name = "wikichess"
        self.host = os.getenv("MILVUS_HOST", "localhost")
        self.port = os.getenv("MILVUS_PORT", "19530")
        
    def connect(self):
        if not connections.has_connection("default"):
            connections.connect("default", host=self.host, port=self.port)

    def init_db(self):
        self.connect()
        if utility.has_collection(self.collection_name):
            return "Déjà initialisé"

        # Configuration du schéma Milvus
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="opening", dtype=DataType.VARCHAR, max_length=100),
            FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=1000),
            FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=384) # dimension pour MiniLM
        ]
        schema = CollectionSchema(fields, description="Base de connaissances Wikichess")
        collection = Collection(self.collection_name, schema)

        # Création de l'index de recherche IVAF_FLAT
        index_params = {
            "metric_type": "L2",
            "index_type": "IVF_FLAT",
            "params": {"nlist": 128}
        }
        collection.create_index(field_name="vector", index_params=index_params)
        
        # Injection de données de démo (Sicilienne, Italienne, Espagnole)
        demo_data = [
            {"opening": "Défense Sicilienne", "text": "La défense sicilienne (1.e4 c5) crée immédiatement une asymétrie pour lutter pour le gain et contrôler la case centrale d4."},
            {"opening": "Partie Italienne", "text": "La partie italienne (1.e4 e5 2.Nf3 Nc6 3.Bc4) développe rapidement le fou blanc pour agresser la case f7."},
            {"opening": "Partie Espagnole", "text": "La partie espagnole ou Ruy Lopez (1.e4 e5 2.Nf3 Nc6 3.Bb5) met la pression sur le cavalier défenseur du centre."}
        ]
        
        texts = [d["text"] for d in demo_data]
        embeddings = self.model.encode(texts).tolist()
        
        ins_data = [
            [d["opening"] for d in demo_data],
            texts,
            embeddings
        ]
        collection.insert(ins_data)
        collection.flush()
        return "Base initialisée avec 3 ouvertures de référence."

    def search(self, query: str):
        self.connect()
        if not utility.has_collection(self.collection_name):
            return []
            
        collection = Collection(self.collection_name)
        collection.load()
        
        query_vector = self.model.encode([query]).tolist()
        search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
        
        results = collection.search(
            data=query_vector, 
            anns_field="vector", 
            param=search_params, 
            limit=1, 
            output_fields=["opening", "text"]
        )
        
        hits = []
        for hits_list in results:
            for hit in hits_list:
                hits.append({
                    "opening": hit.entity.get("opening"),
                    "text": hit.entity.get("text"),
                    "distance": hit.distance
                })
        return hits

rag_service = RAGService()
