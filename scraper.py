import feedparser
from datetime import datetime

SOURCES = {
    "BBC": "http://feeds.bbci.co.uk/news/rss.xml",
    "Dawn": "https://www.dawn.com/feeds/home",
    "Al Jazeera": "https://www.aljazeera.com/xml/rss/all.xml"
}

def get_news(limit=5):
    """
    Scrape news from RSS feeds
    
    Args:
        limit (int): Number of articles per source
        
    Returns:
        list: News items with title, source, content, and timestamp
    """
    all_news = []

    for source_name, url in SOURCES.items():
        try:
            feed = feedparser.parse(url)

            for entry in feed.entries[:limit]:
                news_item = {
                    "title": entry.get("title", ""),
                    "source": source_name,
                    "content": entry.get("summary", entry.get("title", "")),
                    "url": entry.get("link", ""),
                    "published": entry.get("published", ""),
                    "timestamp": datetime.now().isoformat()  # For RAG tracking
                }
                all_news.append(news_item)
                
        except Exception as e:
            print(f"❌ Error fetching from {source_name}: {e}")
            continue

    return all_news
