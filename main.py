"""
 AI NEWS SCRAPER WITH RAG (RETRIEVAL-AUGMENTED GENERATION)

This system:
1. Scrapes news from multiple RSS feeds
2. Stores articles in a vector database
3. Retrieves similar articles for context
4. Generates better summaries using RAG
5. Sends formatted HTML emails

Author: Talal,Abbad,Ahmed
Date: 2026
"""

from scraper import get_news
from summarizer import summarize
from email_sender import send_email
from rag_system import RAGSystem
from datetime import datetime

def main():
    print("\n" + "="*70)
    print(" AI NEWS SCRAPER WITH RAG (RETRIEVAL-AUGMENTED GENERATION)")
    print("="*70)
    
    # Initialize RAG system
    print("\n Initializing RAG system...")
    rag = RAGSystem()
    stats = rag.get_database_stats()
    print(f" Vector database ready! Total stored articles: {stats['total_articles']}")

    # STEP 1: Scrape news
    print("\n Scraping news from BBC, Dawn, Al Jazeera...")
    news = get_news(limit=5)
    print(f" Scraped {len(news)} articles")

    if not news:
        print(" No news scraped. Check your internet connection or RSS feeds.")
        return

    # STEP 2: Summarize with RAG context
    print("\n Summarizing with RAG context...")
    print("(This may take a minute as it retrieves similar articles for context)")
    summaries = summarize(news, rag)

    # STEP 3: Display results
    print("\n" + "="*70)
    print("SUMMARIZED NEWS WITH RAG CONTEXT")
    print("="*70)

    for i, item in enumerate(summaries, start=1):
        print(f"\n NEWS {i}")
        print("="*70)
        print(f"TITLE  : {item['title']}")
        print(f"SOURCE : {item['source']}")
        print("-"*70)
        print("SUMMARY:")
        print(item['summary'])
        
        # Show RAG context information
        if item.get('rag_used'):
            print(f"\n RAG CONTEXT: Found {item.get('related_articles_count')} related articles")
            for j, related in enumerate(item.get('related_articles', [])[:2], 1):
                print(f"   {j}. {related['title'][:60]}... ({related['source']}) - {int(related['similarity_score']*100)}% match")
        else:
            print("\n🔍 RAG CONTEXT: No related articles found (first run or new topic)")
        
        print("="*70)

    # STEP 4: Send email
    print("\n Sending email...")
    send_email(summaries)

    # STEP 5: Summary stats
    print("\n" + "="*70)
    print("✅ PROCESS COMPLETED SUCCESSFULLY!")
    print("="*70)
    print(f" Statistics:")
    print(f"   - Articles scraped: {len(news)}")
    print(f"   - Articles summarized: {len(summaries)}")
    print(f"   - Articles using RAG: {sum(1 for s in summaries if s.get('rag_used'))}")
    print(f"   - Database size: {stats['total_articles']} total articles")
    print(f"   - Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n Program interrupted by user")
    except Exception as e:
        print(f"\n Fatal error: {e}")
        import traceback
        traceback.print_exc()
