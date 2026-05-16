from features.db import DatabaseManager
import json
from pathlib import Path
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', '-d', required=True, help='Directory with JSON files')
    parser.add_argument('--table', '-t', default='papers', help='Table name')
    args = parser.parse_args()
    
    db = DatabaseManager(
        host="localhost",
        port=5432,
        database="my_db",
        user="user",
        password="123"
    )
    
    try:
        if not db.table_exists(args.table):
            db.create_json_table(args.table)
        
        # Pega todos os arquivos .json da pasta
        pasta = Path(args.dir)
        arquivos = list(pasta.glob("*.json"))
        
        print(f"📁 Encontrados {len(arquivos)} arquivos JSON")
        
        for arquivo in arquivos:
            with open(arquivo, 'r', encoding='utf-8') as f:
                article = json.load(f)
            
            db.insert_article(args.table, article)
            print(f"✅ Inserido: {arquivo.name}")
        
    finally:
        db.close()

if __name__ == "__main__":
    main()