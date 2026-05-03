"""
Módulo para gerenciar tabelas JSON no PostgreSQL
Usa psycopg2 para conexão e operações no banco
"""

import psycopg2
from psycopg2 import sql
import json
from typing import List, Dict, Any, Optional

class DatabaseManager:
    """
    Classe para gerenciar conexão e operações no PostgreSQL
    Especializada em tabelas com coluna JSONB
    """
    
    def __init__(self, host: str, port: int, database: str, user: str, password: str):
        """
        Inicializa a conexão com o banco de dados
        
        Args:
            host: Endereço do servidor (ex: localhost)
            port: Porta do PostgreSQL (padrão: 5432)
            database: Nome do banco de dados
            user: Usuário do banco
            password: Senha do banco
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
        self._conectar()
    
    def _conectar(self):
        """Estabelece conexão com o banco de dados"""
        try:
            self.conn = psycopg2.connect(**self.config)
            self.cursor = self.conn.cursor()
            print("✅ Conectado ao banco de dados com sucesso!")
        except psycopg2.Error as e:
            print(f"❌ Erro ao conectar ao banco: {e}")
            raise
    
    def fechar(self):
        """Fecha a conexão com o banco"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("🔌 Conexão fechada")
    
    def criar_tabela_json(self, nome_tabela: str, criar_indices: bool = True) -> bool:
        """
        Cria uma tabela para armazenar dados JSON
        
        Args:
            nome_tabela: Nome da tabela a ser criada
            criar_indices: Se deve criar índice GIN para buscas JSON
        
        Returns:
            True se criou/verificou com sucesso, False caso contrário
        """
        try:
            # SQL para criar tabela
            create_sql = sql.SQL("""
                CREATE TABLE IF NOT EXISTS {} (
                    id SERIAL PRIMARY KEY,
                    titulo VARCHAR(500),
                    autor VARCHAR(200),
                    ano_publicacao INTEGER,
                    conteudo JSONB NOT NULL,
                    data_insercao TIMESTAMP DEFAULT NOW(),
                    data_atualizacao TIMESTAMP DEFAULT NOW()
                )
            """).format(sql.Identifier(nome_tabela))
            
            self.cursor.execute(create_sql)
            
            # Criar índice GIN para buscas JSON (se solicitado)
            if criar_indices:
                index_sql = sql.SQL("""
                    CREATE INDEX IF NOT EXISTS {} ON {} USING GIN (conteudo)
                """).format(
                    sql.Identifier(f"idx_{nome_tabela}_conteudo"),
                    sql.Identifier(nome_tabela)
                )
                self.cursor.execute(index_sql)
                print(f"   ✅ Índice criado para {nome_tabela}")
            
            self.conn.commit()
            print(f"✅ Tabela '{nome_tabela}' criada/verificada com sucesso!")
            return True
            
        except psycopg2.Error as e:
            print(f"❌ Erro ao criar tabela {nome_tabela}: {e}")
            self.conn.rollback()
            return False
    
    def tabela_existe(self, nome_tabela: str) -> bool:
        """Verifica se uma tabela existe no banco"""
        try:
            self.cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = %s
                )
            """, (nome_tabela,))
            return self.cursor.fetchone()[0]
        except psycopg2.Error as e:
            print(f"❌ Erro ao verificar tabela: {e}")
            return False
    
    def listar_tabelas(self) -> List[str]:
        """Retorna lista de todas as tabelas no banco"""
        try:
            self.cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
            return [row[0] for row in self.cursor.fetchall()]
        except psycopg2.Error as e:
            print(f"❌ Erro ao listar tabelas: {e}")
            return []
    
    # def inserir_json(self, nome_tabela: str, json_data: Dict[str, Any], 
    #                  titulo: str = None, autor: str = None, ano: int = None) -> Optional[int]:
    #     """
    #     Insere um documento JSON na tabela
        
    #     Args:
    #         nome_tabela: Tabela onde inserir
    #         json_data: Dicionário com os dados JSON
    #         titulo: Título do artigo (opcional, pode estar no JSON)
    #         autor: Autor do artigo (opcional)
    #         ano: Ano de publicação (opcional)
        
    #     Returns:
    #         ID do registro inserido ou None se erro
    #     """
    #     try:
    #         # Se não passou explicitamente, tenta extrair do JSON
    #         titulo_final = titulo or json_data.get('titulo')
    #         autor_final = autor or json_data.get('autor')
    #         ano_final = ano or json_data.get('ano')
            
    #         insert_sql = sql.SQL("""
    #             INSERT INTO {} (titulo, autor, ano_publicacao, conteudo)
    #             VALUES (%s, %s, %s, %s)
    #             RETURNING id
    #         """).format(sql.Identifier(nome_tabela))
            
    #         self.cursor.execute(insert_sql, (titulo_final, autor_final, ano_final, json.dumps(json_data)))
    #         self.conn.commit()
            
    #         inserted_id = self.cursor.fetchone()[0]
    #         print(f"✅ JSON inserido na tabela '{nome_tabela}' com ID: {inserted_id}")
    #         return inserted_id
            
    #     except psycopg2.Error as e:
    #         print(f"❌ Erro ao inserir JSON: {e}")
    #         self.conn.rollback()
    #         return None
    
    def buscar_json(self, nome_tabela: str, campo: str, valor: str) -> List[Dict]:
        """
        Busca documentos onde um campo do JSON tem um valor específico
        
        Args:
            nome_tabela: Tabela onde buscar
            campo: Nome do campo dentro do JSON
            valor: Valor a ser procurado
        
        Returns:
            Lista de dicionários com os resultados
        """
        try:
            query = sql.SQL("""
                SELECT id, titulo, autor, ano_publicacao, conteudo, data_insercao
                FROM {}
                WHERE conteudo->>%s = %s
                ORDER BY data_insercao DESC
            """).format(sql.Identifier(nome_tabela))
            
            self.cursor.execute(query, (campo, valor))
            resultados = self.cursor.fetchall()
            
            return [
                {
                    "id": row[0],
                    "titulo": row[1],
                    "autor": row[2],
                    "ano": row[3],
                    "conteudo": row[4],
                    "data_insercao": row[5]
                }
                for row in resultados
            ]
        except psycopg2.Error as e:
            print(f"❌ Erro na busca: {e}")
            return []
    
    # def deletar_todos(self, nome_tabela: str) -> bool:
    #     """Remove todos os registros de uma tabela (mantém a estrutura)"""
    #     try:
    #         resposta = input(f"⚠️ Tem certeza que quer deletar TODOS os dados da tabela '{nome_tabela}'? (s/N): ")
    #         if resposta.lower() == 's':
    #             self.cursor.execute(sql.SQL("DELETE FROM {}").format(sql.Identifier(nome_tabela)))
    #             self.conn.commit()
    #             print(f"✅ Todos os dados deletados da tabela '{nome_tabela}'")
    #             return True
    #         else:
    #             print("❌ Operação cancelada")
    #             return False
    #     except psycopg2.Error as e:
    #         print(f"❌ Erro ao deletar dados: {e}")
    #         self.conn.rollback()
    #         return False
    
    # def deletar_tabela(self, nome_tabela: str) -> bool:
    #     """Remove a tabela inteira"""
    #     try:
    #         resposta = input(f"⚠️ Tem certeza que quer deletar a TABELA '{nome_tabela}'? (s/N): ")
    #         if resposta.lower() == 's':
    #             self.cursor.execute(sql.SQL("DROP TABLE IF EXISTS {} CASCADE").format(sql.Identifier(nome_tabela)))
    #             self.conn.commit()
    #             print(f"✅ Tabela '{nome_tabela}' deletada com sucesso!")
    #             return True
    #         else:
    #             print("❌ Operação cancelada")
    #             return False
    #     except psycopg2.Error as e:
    #         print(f"❌ Erro ao deletar tabela: {e}")
    #         self.conn.rollback()
    #         return False
    
    def inserir_artigo(self, nome_tabela: str, artigo_json: Dict) -> Optional[int]:
        """Insere um artigo, evitando duplicatas por DOI"""
        try:
            titulo = artigo_json.get('title')
            ano = artigo_json.get('publication_date')
            doi = artigo_json.get('doi')
            
            # Verificar se já existe pelo DOI
            if doi:
                self.cursor.execute(f"""
                    SELECT id FROM {nome_tabela} 
                    WHERE conteudo->>'doi' = %s
                """, (doi,))
                
                existing = self.cursor.fetchone()
                if existing:
                    print(f"⚠️ Artigo já existe (ID: {existing[0]}). Pulando inserção.")
                    return existing[0]
            
            # Extrair autores
            autores_lista = artigo_json.get('authors', [])
            if autores_lista and isinstance(autores_lista[0], dict):
                autores = ", ".join([a.get('name', '') for a in autores_lista])
            else:
                autores = ", ".join(autores_lista) if autores_lista else None
            
            # Inserir
            self.cursor.execute(f"""
                INSERT INTO {nome_tabela} (titulo, autor, ano_publicacao, conteudo)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            """, (titulo, autores, ano, json.dumps(artigo_json)))
            
            self.conn.commit()
            inserted_id = self.cursor.fetchone()[0]
            print(f"✅ Artigo inserido (ID: {inserted_id})")
            return inserted_id
            
        except psycopg2.Error as e:
            print(f"❌ Erro: {e}")
            return None