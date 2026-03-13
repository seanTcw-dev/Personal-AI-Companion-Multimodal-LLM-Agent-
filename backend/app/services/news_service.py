
import random
from typing import List, Dict
from datetime import datetime

class MockNewsService:
    def __init__(self):
        self.current_news_batch = []
        self.refresh_news(5) # Initialize with some news

    def get_latest_news(self, limit: int = 5) -> List[Dict]:
        """Returns the *current* batch of news. Does NOT auto-generate new ones on every call."""
        if not self.current_news_batch:
            self.refresh_news(limit)
        return self.current_news_batch[:limit]

    def refresh_news(self, limit: int = 5) -> List[Dict]:
        """Manually triggers generation of a new batch of news."""
        
        # Cyberpunk / Tech themed news headlines
        HEADLINES = [
            "Global AI Regulation Summit reaches historic agreement",
            "NeuralLink v4 implants explicitly banned in competitive gaming",
            "SpaceX Mars Colony 'Ares' welcomes its 1000th resident",
            "Quantum Computing breakthrough: Encryption standards updated overnight",
            "New 'Holo-Phone' prototype leaked by Apple insider",
            "Bitcoin hits new all-time high of $150k amid digital currency adoption",
            "Virtual Reality addiction classified as a global health crisis",
            "Climate 'Reversal' project shows promising results in the Arctic",
            "Hackers compromise 'Smart City' traffic grid, causing chaos in Neo-Tokyo",
            "Anime waifus are now legally recognized as emotional support companions in Japan",
            "Corporations now buying voting rights in new UN charter",
            "Flying car regulations stalled indefinitely due to air traffic concerns",
            "Underground net-runners expose massive data leak at BioTech Inc.",
            "Synthetics rights movement gains traction in Europe",
            "First AI-directed movie wins Palme d'Or at Cannes"
        ]

        news_items = []
        # Randomly select new headlines
        selected_headlines = random.sample(HEADLINES, min(limit, len(HEADLINES)))
        
        for i, title in enumerate(selected_headlines):
            news_items.append({
                "id": f"news-{int(datetime.now().timestamp())}-{i}",
                "title": title,
                "source": random.choice(["TechCrunch", "BBC Future", "Neon Times", "The Verge", "Reuters"]),
                "timestamp": datetime.now().isoformat(),
                "summary": f"In a shocking turn of events, {title.lower()}... Experts say this could change everything. The impact on the global market is yet to be seen."
            })
            
        self.current_news_batch = news_items
        return self.current_news_batch

news_service = MockNewsService()
