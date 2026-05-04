"""
Módulo para gerenciar tabelas JSON no PostgreSQL
Usa psycopg2 para conexão e operações no banco
"""

import psycopg2
from psycopg2 import sql
import json
from typing import List, Dict, Optional

class DatabaseManager:
    """
    Class to manage PostgreSQL connections and operations.
    Specialized in tables with JSONB columns.
    """
    
    def __init__(self, host: str, port: int, database: str, user: str, password: str):
        """
        Initializes the database connection.
        
        Args:
            host: Server address (e.g., localhost)
            port: PostgreSQL port (default: 5432)
            database: Database name
            user: Database user
            password: Database password
        """
        self.config = {
            "host": host,
            "port": port,
            "database": database,
            "user": user,
            "password": password
        }
        self.conn = None
        self.cursor = None
        self._connect()

    def _connect(self):
        """
        Establishes connection to the database.
        
        Raises:
            psycopg2.Error: If connection fails
        """
        try:
            self.conn = psycopg2.connect(**self.config)
            self.cursor = self.conn.cursor()
            print("✅ Successfully connected to the database!")
        except psycopg2.Error as e:
            print(f"❌ Error connecting to the database: {e}")
            raise

    def close(self):
        """
        Closes the database connection.
        """
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("🔌 Connection closed")
    
    def create_json_table(self, table_name: str, create_indexes: bool = True) -> bool:
        """
        Creates a table with columns for main metadata, summary, bibtex, and secondary metadata.
        
        Args:
            table_name: Name of the table to be created
            create_indexes: Whether to create GIN indexes for JSON searches
        
        Returns:
            True if created/verified successfully, False otherwise
        """
        try:
            create_sql = sql.SQL("""
                CREATE TABLE IF NOT EXISTS {} (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(500),
                    author VARCHAR(200),
                    publication_year INTEGER,
                    doi VARCHAR(100),
                    summary JSONB,
                    bibtex_citation TEXT,
                    metadata JSONB NOT NULL,
                    insertion_date TIMESTAMP DEFAULT NOW(),
                    update_date TIMESTAMP DEFAULT NOW()
                )
            """).format(sql.Identifier(table_name))
            
            self.cursor.execute(create_sql)
            
            if create_indexes:
                # Indexes for fast searches
                self.cursor.execute(sql.SQL(
                    "CREATE INDEX IF NOT EXISTS {} ON {} (doi)"
                ).format(sql.Identifier(f"idx_{table_name}_doi"), sql.Identifier(table_name)))
                
                self.cursor.execute(sql.SQL(
                    "CREATE INDEX IF NOT EXISTS {} ON {} USING GIN (summary)"
                ).format(sql.Identifier(f"idx_{table_name}_summary"), sql.Identifier(table_name)))
                
                self.cursor.execute(sql.SQL(
                    "CREATE INDEX IF NOT EXISTS {} ON {} USING GIN (metadata)"
                ).format(sql.Identifier(f"idx_{table_name}_metadata"), sql.Identifier(table_name)))
                
                # Index for bibtex searches (if needed)
                self.cursor.execute(sql.SQL(
                    "CREATE INDEX IF NOT EXISTS {} ON {} (bibtex_citation)"
                ).format(sql.Identifier(f"idx_{table_name}_bibtex"), sql.Identifier(table_name)))
                
                print(f"   ✅ Indexes created")
            
            self.conn.commit()
            print(f"✅ Table '{table_name}' created")
            print(f"   Columns: id, title, author, year, doi, summary, bibtex_citation, metadata")
            return True
            
        except psycopg2.Error as e:
            print(f"❌ Error: {e}")
            self.conn.rollback()
            return False
    
    def table_exists(self, table_name: str) -> bool:
        """
        Checks if a table exists in the database.
        
        Args:
            table_name: Name of the table to check
        
        Returns:
            True if the table exists, False otherwise
        """
        try:
            self.cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = %s
                )
            """, (table_name,))
            return self.cursor.fetchone()[0]
        except psycopg2.Error as e:
            print(f"❌ Error checking table existence: {e}")
            return False
        
    def list_tables(self) -> List[str]:
        """
        Returns a list of all tables in the database.
        
        Returns:
            List of table names. Returns empty list if an error occurs.
        """
        try:
            self.cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
            return [row[0] for row in self.cursor.fetchall()]
        except psycopg2.Error as e:
            print(f"❌ Error listing tables: {e}")
            return []
    
    def search_json(self, table_name: str, field: str, value: str) -> List[Dict]:
        """
        Searches for documents where a JSON field has a specific value.
        
        Args:
            table_name: Table where to search
            field: Field name inside the JSON
            value: Value to search for
        
        Returns:
            List of dictionaries with the results. Returns empty list if an error occurs.
        """
        try:
            query = sql.SQL("""
                SELECT id, title, author, publication_year, doi, summary, metadata, insertion_date
                FROM {}
                WHERE metadata->>%s = %s
                ORDER BY insertion_date DESC
            """).format(sql.Identifier(table_name))
            
            self.cursor.execute(query, (field, value))
            results = self.cursor.fetchall()
            
            return [
                {
                    "id": row[0],
                    "title": row[1],
                    "author": row[2],
                    "year": row[3],
                    "doi": row[4],
                    "summary": row[5],
                    "metadata": row[6],
                    "insertion_date": row[7]
                }
                for row in results
            ]
        except psycopg2.Error as e:
            print(f"❌ Error during search: {e}")
            return []
    
    def search_by_doi(self, table_name: str, doi: str) -> Optional[Dict]:
        """
        Searches for an article by its DOI.
        
        Args:
            table_name: Table where to search
            doi: DOI of the article
        
        Returns:
            Dictionary with the article data if found, None otherwise
        """
        try:
            query = sql.SQL("""
                SELECT id, title, author, publication_year, doi, summary, bibtex_citation, metadata, insertion_date
                FROM {}
                WHERE doi = %s
            """).format(sql.Identifier(table_name))
            
            self.cursor.execute(query, (doi,))
            row = self.cursor.fetchone()
            
            if row:
                return {
                    "id": row[0],
                    "title": row[1],
                    "author": row[2],
                    "year": row[3],
                    "doi": row[4],
                    "summary": row[5],
                    "bibtex_citation": row[6],
                    "metadata": row[7],
                    "insertion_date": row[8]
                }
            return None
            
        except psycopg2.Error as e:
            print(f"❌ Error during search: {e}")
            return None

    def insert_article(self, table_name: str, article_json: Dict) -> Optional[int]:
        """
        Inserts an article by separating:
        - Main columns: title, author, year, doi
        - Summary column: complete summary object
        - BibTeX column: BibTeX citation
        - Metadata column: ONLY secondary metadata (journal, keywords, etc.)
        
        Args:
            table_name: Table where to insert
            article_json: Dictionary with the article JSON data
        
        Returns:
            ID of the inserted or existing article, None if error
        """
        try:
            # 1. Extract main metadata (goes to columns)
            title = article_json.get('title')
            year = article_json.get('publication_date')
            doi = article_json.get('doi')
            
            # 2. Extract summary (goes to summary column)
            summary = article_json.get('summary')
            
            # 3. Extract bibtex_citation (goes to bibtex_citation column)
            bibtex_citation = article_json.get('bibtex_citation')
            
            # 4. Extract authors for author column
            authors_list = article_json.get('authors', [])
            if authors_list and isinstance(authors_list[0], dict):
                author = ", ".join([a.get('name', '') for a in authors_list])
            else:
                author = ", ".join(authors_list) if authors_list else None
            
            # 5. Create 'metadata' object with the REMAINING data
            metadata_json = {}
            
            # Fields that go to metadata (everything not extracted)
            metadata_fields = [
                'journal', 'volume', 'issue', 'pages', 'publisher',
                'language', 'issn', 'isbn', 'url', 'pdf_url',
                'keywords', 'palavras_chave', 'tags',
                'references', 'citations',
                '_metadata', 'source_file', 'model', 'timestamp'
            ]
            
            for field in metadata_fields:
                if field in article_json:
                    metadata_json[field] = article_json[field]
            
            # Include any other fields not extracted
            extracted_fields = {'title', 'publication_date', 'doi', 'authors', 'summary', 'bibtex_citation'}
            for field, value in article_json.items():
                if field not in extracted_fields and field not in metadata_json:
                    metadata_json[field] = value
            
            # 6. Check for duplicates by DOI
            if doi:
                self.cursor.execute(f"SELECT id FROM {table_name} WHERE doi = %s", (doi,))
                existing = self.cursor.fetchone()
                if existing:
                    print(f"⚠️ Article already exists (ID: {existing[0]}). Skipping insertion.")
                    return existing[0]
            
            # 7. Insert
            self.cursor.execute(f"""
                INSERT INTO {table_name} 
                (title, author, publication_year, doi, summary, bibtex_citation, metadata)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                title, 
                author, 
                year, 
                doi, 
                json.dumps(summary) if summary else None,
                bibtex_citation,
                json.dumps(metadata_json)
            ))
            
            self.conn.commit()
            inserted_id = self.cursor.fetchone()[0]
            
            print(f"✅ Article inserted (ID: {inserted_id})")
            print(f"   📌 Title: {title}")
            print(f"   📌 DOI: {doi}")
            print(f"   📋 Summary: {'Yes' if summary else 'No'}")
            print(f"   📖 BibTeX: {'Yes' if bibtex_citation else 'No'}")
            print(f"   📦 Metadata: {len(metadata_json)} fields")
            return inserted_id
            
        except psycopg2.Error as e:
            print(f"❌ Error inserting article: {e}")
            self.conn.rollback()
            return None
            
        except psycopg2.Error as e:
            print(f"❌ Erro: {e}")
            self.conn.rollback()
            return None
    
    # def atualizar_tabela(self, nome_tabela: str) -> bool:
    #     """
    #     Atualiza uma tabela existente adicionando as colunas DOI e Summary
    #     Útil para migrar tabelas antigas
    #     """
    #     try:
    #         # Verificar se a coluna doi existe
    #         self.cursor.execute("""
    #             SELECT column_name 
    #             FROM information_schema.columns 
    #             WHERE table_name = %s AND column_name = 'doi'
    #         """, (nome_tabela,))
            
    #         if not self.cursor.fetchone():
    #             self.cursor.execute(f"""
    #                 ALTER TABLE {nome_tabela} 
    #                 ADD COLUMN doi VARCHAR(100),
    #                 ADD COLUMN summary JSONB
    #             """)
    #             self.conn.commit()
    #             print(f"✅ Colunas 'doi' e 'summary' adicionadas à tabela '{nome_tabela}'")
                
    #             # Opcional: popular as novas colunas com dados do JSON existente
    #             self.cursor.execute(f"""
    #                 UPDATE {nome_tabela} 
    #                 SET doi = conteudo->>'doi',
    #                     summary = conteudo->'summary'
    #                 WHERE doi IS NULL
    #             """)
    #             self.conn.commit()
    #             print(f"   ✅ Dados migrados para as novas colunas")
    #             return True
    #         else:
    #             print(f"⚠️ Tabela '{nome_tabela}' já possui as colunas DOI e Summary")
    #             return True
                
    #     except psycopg2.Error as e:
    #         print(f"❌ Erro ao atualizar tabela: {e}")
    #         self.conn.rollback()
    #         return False