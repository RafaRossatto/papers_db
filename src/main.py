"""
Script para criar a tabela 'papers' no banco de dados PostgreSQL
A tabela é projetada para armazenar artigos sumarizados em formato JSON
"""

import psycopg2
from psycopg2 import sql

# Configuração de conexão com o banco
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "my_db",
    "user": "user",
    "password": "123"
}

# SQL para criar a tabela papers
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS papers (
    id SERIAL PRIMARY KEY,
    titulo VARCHAR(500),
    autor VARCHAR(200),
    ano_publicacao INTEGER,
    conteudo JSONB NOT NULL,
    data_insercao TIMESTAMP DEFAULT NOW(),
    data_atualizacao TIMESTAMP DEFAULT NOW()
);

-- Criar índice para busca eficiente em JSONB
CREATE INDEX IF NOT EXISTS idx_papers_conteudo ON papers USING GIN (conteudo);

-- Comentários para documentação
COMMENT ON TABLE papers IS 'Armazena artigos sumarizados em formato JSON';
COMMENT ON COLUMN papers.id IS 'Identificador único do artigo';
COMMENT ON COLUMN papers.titulo IS 'Título do artigo (extraído do JSON)';
COMMENT ON COLUMN papers.autor IS 'Autor principal do artigo';
COMMENT ON COLUMN papers.ano_publicacao IS 'Ano de publicação do artigo';
COMMENT ON COLUMN papers.conteudo IS 'JSON completo com todos os dados do artigo';
COMMENT ON COLUMN papers.data_insercao IS 'Data de inserção no banco';
COMMENT ON COLUMN papers.data_atualizacao IS 'Data da última atualização';
"""

def criar_tabela():
    """Cria a tabela papers no banco de dados"""
    try:
        # Conectar ao banco
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # Executar o SQL
        cur.execute(CREATE_TABLE_SQL)
        
        # Confirmar a transação
        conn.commit()
        
        print("✅ Tabela 'papers' criada com sucesso!")
        print("   - Coluna 'id' (auto-incremento)")
        print("   - Coluna 'titulo' (texto)")
        print("   - Coluna 'autor' (texto)")
        print("   - Coluna 'ano_publicacao' (inteiro)")
        print("   - Coluna 'conteudo' (JSONB)")
        print("   - Coluna 'data_insercao' (timestamp)")
        print("   - Coluna 'data_atualizacao' (timestamp)")
        print("\n✅ Índice GIN criado para buscas eficientes em JSONB")
        
        cur.close()
        conn.close()
        
    except psycopg2.Error as e:
        print(f"❌ Erro ao criar tabela: {e}")
        return False
    
    return True

def verificar_tabela():
    """Verifica se a tabela foi criada corretamente"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # Verificar se a tabela existe
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'papers'
            );
        """)
        
        existe = cur.fetchone()[0]
        
        if existe:
            print("\n✅ Tabela 'papers' existe no banco!")
            
            # Mostrar estrutura
            cur.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'papers'
                ORDER BY ordinal_position;
            """)
            
            print("\n📋 Estrutura da tabela:")
            print("-" * 50)
            for coluna, tipo, nulo in cur.fetchall():
                print(f"   {coluna:20} | {tipo:20} | Null: {nulo}")
        else:
            print("\n❌ Tabela 'papers' não encontrada!")
        
        cur.close()
        conn.close()
        
    except psycopg2.Error as e:
        print(f"❌ Erro ao verificar tabela: {e}")

if __name__ == "__main__":
    print("🚀 Criando tabela 'papers' no banco de dados...\n")
    
    if criar_tabela():
        verificar_tabela()
    else:
        print("\n❌ Falha ao criar a tabela.")