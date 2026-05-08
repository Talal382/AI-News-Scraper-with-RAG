import chromadb

# 1. Connect to the database folder
client = chromadb.PersistentClient(path="./chroma_data")

try:
    # 2. Use the correct name: "news_articles"
    collection = client.get_collection(name="news_articles")

    # 3. Get total count
    total_count = collection.count()
    print(f"\n📊 TOTAL ITEMS IN DATABASE: {total_count}")
    print("=" * 50)

    # 4. Peek at the first 10 items
    if total_count > 0:
        first_10 = collection.peek(limit=10)
        print("🔍 PREVIEW: FIRST 10 ARTICLES")
        print("-" * 50)

        for i in range(len(first_10['ids'])):
            print(f"[{i+1}] ID: {first_10['ids'][i]}")
            print(f"    TITLE: {first_10['metadatas'][i]['title']}")
            print(f"    SOURCE: {first_10['metadatas'][i]['source']}")
            print(f"    TEXT: {first_10['documents'][i][:75]}...")
            print("-" * 50)
    else:
        print("The database is currently empty.")

except Exception as e:
    print(f"❌ Error: {e}")
    print("Check if the collection name in rag_system.py is exactly 'news_articles'.")