from features.db import DatabaseManager
import json

def main():

    # 1. Criar instância (já conecta)
    db = DatabaseManager(
        host="localhost",
        port=5432,
        database="my_db",
        user="user",
        password="123"
    )

    try:
        # 2. Definir o nome da tabela
        nome_tabela = "papers"
        
        # 3. Verificar se a tabela existe, se não, criar
        if not db.tabela_existe(nome_tabela):
            print(f"📦 Tabela '{nome_tabela}' não existe. Criando...")
            db.criar_tabela_json(nome_tabela)
        else:
            print(f"✅ Tabela '{nome_tabela}' já existe. Usando ela.")
        
        # 4. Carregar o JSON do arquivo
        with open('/home/rafarossatto/personal_projects/pdf-summarizer-agent/src/outputs/aria2017.json', 'r', encoding='utf-8') as f:
            artigo = json.load(f)
        
        # 5. Inserir usando o método inserir_artigo da classe
        artigo_id = db.inserir_artigo(nome_tabela, artigo)
        
        if artigo_id:
            print(f"\n📊 Resumo do artigo inserido:")
            print(f"   ID: {artigo_id}")
            print(f"   Título: {artigo.get('title')}")
            print(f"   DOI: {artigo.get('doi')}")
            print(f"   Journal: {artigo.get('journal')}")
            
            # Mostrar primeiros autores
            autores = artigo.get('authors', [])
            if autores:
                primeiro_autor = autores[0].get('name') if isinstance(autores[0], dict) else autores[0]
                print(f"   Primeiro autor: {primeiro_autor}")
        
        # 6. Opcional: Buscar para confirmar
        print("\n🔍 Buscando artigos com DOI específico...")
        resultados = db.buscar_json(nome_tabela, "doi", "10.1016/j.joi.2017.08.007")
        
        for item in resultados:
            print(f"\n✅ Encontrado:")
            print(f"   ID: {item['id']}")
            print(f"   Título: {item['titulo']}")
            print(f"   Autor: {item['autor']}")

    finally:
        # 7. Fechar conexão
        db.fechar()

if __name__ == "__main__":
    main()