from groq import Groq
import os
import re
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def summarize(news_list, rag):
    """
    Summarize news articles with RAG context and prevent duplicates.
    """
    summaries = []

    for idx, news in enumerate(news_list):
        title = news["title"]
        source = news["source"]
        content = news["content"]
        timestamp = news.get("timestamp", "")
        url = news.get("url", "")  # Get URL from news item
        
        print(f"\n Processing: {title[:60]}...")

        # STEP 1: Retrieve similar articles from vector database (RAG)
        query_text = f"{title}. {content}"
        similar_articles = rag.retrieve_similar_articles(query_text, num_results=3)
        
        # Format similar articles for the prompt
        context_str = ""
        if similar_articles:
            context_str = "\n RELATED ARTICLES FOR CONTEXT:\n"
            for i, article in enumerate(similar_articles, 1):
                context_str += f"\n{i}. {article['title']} (Source: {article['source']})\n"
                context_str += f"   Summary: {article['summary'][:150]}...\n"
                context_str += f"   Similarity: {article['similarity_score']*100:.0f}%\n"

        # STEP 2: Create enhanced prompt with RAG context
        prompt = f"""
You are a professional news summarizer with knowledge of recent events.

RECENT RELATED ARTICLES FOR CONTEXT:
{context_str if context_str else "No related articles found in database."}

NEW ARTICLE TO SUMMARIZE:
Title: {title}
Source: {source}
Content: {content}

INSTRUCTIONS:
1. Do NOT repeat instructions or add preambles
2. Write a 3-4 line factual summary ONLY
3. If related articles exist, explain how this relates to them
4. Each line should contain real information from the news

Output ONLY the summary, nothing else:
"""

        try:
            # STEP 3: Call Groq API
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=200
            )

            summary_text = response.choices[0].message.content
            
            # STEP 4: Create a unique ID based on the title to prevent duplicates
            # This removes special characters and spaces
            clean_title_id = re.sub(r'[^a-zA-Z0-9]', '', title).lower()[:50]
            article_id = f"{source}_{clean_title_id}"
            
            # Store article (the RAG system will now handle the duplicate check)
            rag.store_article(
                article_id=article_id,
                title=title,
                content=content,
                source=source,
                summary=summary_text,
                timestamp=timestamp
            )

            summaries.append({
                "title": title,
                "source": source,
                "summary": summary_text,
                "url": url,  # Include URL in summary
                "related_articles_count": len(similar_articles),
                "related_articles": similar_articles,
                "rag_used": len(similar_articles) > 0
            })
            
            print(f" Finished: {title[:40]}...")

        except Exception as e:
            print(f" Error summarizing: {e}")
            summaries.append({
                "title": title,
                "source": source,
                "summary": f"Error: Could not summarize this article",
                "url": url,  # Include URL even in error case
                "related_articles_count": 0,
                "related_articles": [],
                "rag_used": False
            })

    return summaries
