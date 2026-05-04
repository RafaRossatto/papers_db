from features.db import DatabaseManager
import json

def main():
    """
    Main function to insert an article JSON into the database.
    """
    # 1. Create instance (already connects)
    db = DatabaseManager(
        host="localhost",
        port=5432,
        database="my_db",
        user="user",
        password="123"
    )

    try:
        # 2. Define the table name
        table_name = "papers"
        
        # 3. Check if the table exists, if not, create it
        if not db.table_exists(table_name):
            print(f"📦 Table '{table_name}' does not exist. Creating...")
            db.create_json_table(table_name)
        else:
            print(f"✅ Table '{table_name}' already exists. Using it.")
        
        # 4. Load JSON from file
        with open('/home/rafarossatto/personal_projects/pdf-summarizer-agent/src/outputs/aria2017.json', 'r', encoding='utf-8') as f:
            article = json.load(f)
        
        # 5. Insert using the class method insert_article
        article_id = db.insert_article(table_name, article)
        
        if article_id:
            print(f"\n📊 Summary of inserted article:")
            print(f"   ID: {article_id}")
            print(f"   Title: {article.get('title')}")
            print(f"   DOI: {article.get('doi')}")
            print(f"   Journal: {article.get('journal')}")
            
            # Show first author
            authors = article.get('authors', [])
            if authors:
                first_author = authors[0].get('name') if isinstance(authors[0], dict) else authors[0]
                print(f"   First author: {first_author}")
        
        # # 6. Optional: Search to confirm
        # print("\n🔍 Searching for articles with specific DOI...")
        # results = db.search_json(table_name, "doi", "10.1016/j.joi.2017.08.007")
        
        # for item in results:
        #     print(f"\n✅ Found:")
        #     print(f"   ID: {item['id']}")
        #     print(f"   Title: {item['title']}")
        #     print(f"   Author: {item['author']}")

    finally:
        # 7. Close connection
        db.close()

if __name__ == "__main__":
    main()