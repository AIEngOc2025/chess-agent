import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymilvus import connections

class DatabaseManager:
    def __init__(self):
        self.mongo_client = None
        self.db = None

    async def connect(self):
        print("🚀 Connexion aux bases de données...")
        
        # 1. MongoDB (Obligation du livrable)
        mongo_uri = os.getenv("MONGO_URI", "mongodb://admin:secret@chess_mongodb:27017")
        self.mongo_client = AsyncIOMotorClient(mongo_uri)
        self.db = self.mongo_client["chess_database"]
        print("✔ MongoDB : Connecté.")

        # 2. Milvus (Étape 3 RAG)
        milvus_host = os.getenv("MILVUS_HOST", "milvus-standalone")
        milvus_port = os.getenv("MILVUS_PORT", "19530")
        connections.connect("default", host=milvus_host, port=milvus_port)
        print(f"✔ Milvus : Connecté sur le port {milvus_port}.")

    async def disconnect(self):
        if self.mongo_client:
            self.mongo_client.close()
            print("🛑 MongoDB : Connexion fermée.")
        try:
            connections.disconnect("default")
            print("🛑 Milvus : Déconnecté.")
        except Exception:
            pass

# Instance unique (Singleton)
db_manager = DatabaseManager()