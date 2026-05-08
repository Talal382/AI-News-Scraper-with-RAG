import chromadb
import os

class RAGSystem:
    def __init__(self, db_path="./chroma_data"):
        self.db_path = db_path
        os.makedirs(db_path, exist_ok=True)
        
        # Initialize persistent client
        self.client = chromadb.PersistentClient(path=db_path)
        
        self.collection = self.client.get_or_create_collection(
            name="news_articles",
            metadata={"hnsw:space": "cosine"}
        )
    
    def store_article(self, article_id, title, content, source, summary, timestamp):
        """
        Stores article but checks for duplicates first.
        """
        try:
            # Check if ID already exists
            existing = self.collection.get(ids=[article_id])
            if existing and existing['ids']:
                print(f"⏩ Skipping Storage: Article already exists in DB.")
                return

            text_to_embed = f"{title}. {content}"
            
            self.collection.add(
                ids=[article_id],
                documents=[text_to_embed],
                metadatas=[{
                    "title": title,
                    "source": source,
                    "summary": summary,
                    "timestamp": timestamp,
                    "content_preview": content[:200]
                }]
            )
            print(f"✅ Stored in vector DB: {title[:40]}...")
            
        except Exception as e:
            print(f"⚠️ Error storing article: {e}")
    
    def retrieve_similar_articles(self, query_text, num_results=3):
        try:
            if self.collection.count() == 0:
                return []

            results = self.collection.query(
                query_texts=[query_text],
                n_results=num_results
            )
            
            similar_articles = []
            if results and results['metadatas'] and len(results['metadatas'][0]) > 0:
                for i, metadata in enumerate(results['metadatas'][0]):
                    # If distance is near 0, it's the exact same story
                    if results['distances'][0][i] > 0.05: 
                        similar_articles.append({
                            "title": metadata.get("title", ""),
                            "source": metadata.get("source", ""),
                            "summary": metadata.get("summary", ""),
                            "timestamp": metadata.get("timestamp", ""),
                            "similarity_score": round(1 - results['distances'][0][i], 2)
                        })
            
            return similar_articles
        except Exception as e:
            print(f"⚠️ Error retrieving: {e}")
            return []
    
    def get_database_stats(self):
        try:
            return {"total_articles": self.collection.count()}
        except:
            return {"total_articles": 0}