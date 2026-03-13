"""
News API Routes
Handles news-related endpoints (mock news service)
"""
from fastapi import APIRouter, Query

router = APIRouter()


@router.get("/news")
async def get_news(limit: int = Query(default=5)):
    """Get latest news"""
    from app.services.news_service import news_service

    news = news_service.get_latest_news(limit=limit)
    return {
        "news": news
    }


@router.post("/news/refresh")
async def refresh_news(limit: int = Query(default=5)):
    """Refresh news - generate a new batch of headlines"""
    from app.services.news_service import news_service

    news = news_service.refresh_news(limit=limit)
    return {
        "news": news,
        "message": f"Refreshed {len(news)} news items"
    }
