import warnings
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# Ignorar os avisos do HuggingFace para manter o terminal limpo no teste
warnings.filterwarnings("ignore")

print("⏳ 1. A carregar o modelo de embeddings (isto pode demorar uns segundos)...")
embeddings = HuggingFaceEmbeddings(
    model_name="intfloat/multilingual-e5-large",
    model_kwargs={'device': 'cpu'}
)

caminho_bd = r"C:\Users\berna\Processo_RAG_contabilista_11-03-26\chroma_db_municipios"

print(f"📂 2. A ligar à base de dados em: {caminho_bd}")
try:
    vector_db = Chroma(
        persist_directory=caminho_bd, 
        embedding_function=embeddings, 
        collection_name="contabilidade_portuguesa"
    )
    
    # Aceder à coleção interna do Chroma para contar os documentos
    total_docs = vector_db._collection.count()
    
    print("\n" + "="*50)
    print("✅ SUCESSO: Ligação à base de dados estabelecida!")
    print(f"📊 Total de chunks (documentos) guardados: {total_docs}")
    print("="*50)

    if total_docs > 0:
        print("\n🔍 3. A fazer um teste de pesquisa rápido pela palavra 'despesa'...")
        # Pesquisar apenas os 2 resultados mais relevantes
        resultados = vector_db.similarity_search("despesa", k=2)
        
        for i, doc in enumerate(resultados):
            print(f"\n--- 📦 RESULTADO {i+1} ---")
            print(f"📑 Metadados (Origem): {doc.metadata}")
            # Mostrar apenas os primeiros 300 caracteres para não inundar o terminal
            print(f"📝 Excerto do texto: {doc.page_content[:300]}...") 
    else:
        print("\n⚠️ AVISO: A tua base de dados ligou com sucesso, mas está VAZIA (0 documentos).")
        print("Terás de correr o teu script de ingestão (criação da base de dados) novamente.")

except Exception as e:
    print(f"\n❌ ERRO ao tentar ligar à base de dados: {e}")