import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class YouTubeService:
    def __init__(self):
        # Récupération de la clé API depuis l'environnement Docker
        self.api_key = os.getenv("YOUTUBE_API_KEY", "")
        self.youtube = build("youtube", "v3", developerKey=self.api_key) if self.api_key else None

    def search_videos(self, opening_name: str):
        """Recherche des vidéos pédagogiques sur YouTube pour une ouverture donnée."""
        if not self.youtube:
            return [{
                "video_id": "mock_id",
                "title": f"[Mode Démo] Tuto pour l'ouverture : {opening_name}",
                "description": "Configurez YOUTUBE_API_KEY pour obtenir de vrais résultats.",
                "channel_name": "Chaîne FFE",
                "thumbnail_url": "https://images.unsplash.com/photo-1529699211952-734e80c4d42b",
                "video_url": "https://www.youtube.com/watch?v=mock_id",
                "embed_url": "https://www.youtube.com/embed/mock_id"
            }]

        try:
            # Construction d'une requête pertinente mixant le nom et des mots-clés d'échecs
            query = f"chess opening {opening_name} tutorial explanation"
            
            request = self.youtube.search().list(
                q=query,
                part="snippet",
                type="video",
                maxResults=2,  # Évite de gaspiller les quotas inutilement
                videoEmbeddable="true"  # Point de vigilance : s'assurer que l'intégration est possible
            )
            response = request.execute()
            
            videos = []
            for item in response.get("items", []):
                video_id = item["id"]["videoId"]
                snippet = item["snippet"]
                videos.append({
                    "video_id": video_id,
                    "title": snippet["title"],
                    "description": snippet["description"],
                    "channel_name": snippet["channelTitle"],
                    "thumbnail_url": snippet["thumbnails"]["high"]["url"],
                    "video_url": f"https://www.youtube.com/watch?v={video_id}",
                    "embed_url": f"https://www.youtube.com/embed/{video_id}"
                })
            return videos

        except HttpError as e:
            # En cas d'erreur de quotas ou clé invalide, on renvoie une liste vide proprement
            print(f"Erreur API YouTube : {e}")
            return []

youtube_service = YouTubeService()
