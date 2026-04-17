import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

logging.basicConfig(level=logging.WARNING)

os.environ["GOOGLE_API_KEY"] = "AIzaSyDPiz7ikditkr4DS8xcu81e6UielcaKtIg" # Lembra-te de ocultar isto depois!

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.1)

# Inicializar o servidor Flask
app = Flask(__name__)
CORS(app) # Permite pedidos do XAMPP

def pesquisar_base_aberta(pergunta):
    embeddings = HuggingFaceEmbeddings(
        model_name="intfloat/multilingual-e5-large",
        model_kwargs={'device': 'cpu'}
    )
    
    caminho_bd = r"C:\Users\berna\RAG_livro_ORDEM_CONTABILISTAS\bd_vetorial"    
    vector_db = Chroma(
        persist_directory=caminho_bd, 
        embedding_function=embeddings, 
        collection_name="contabilidade_portuguesa"
    )
    
    resultados = vector_db.similarity_search(pergunta, k=5)
    contexto_recuperado = "\n\n".join([doc.page_content for doc in resultados])
    return contexto_recuperado

def executar_pergunta(pergunta):
    contexto = pesquisar_base_aberta(pergunta)

    prompt = f"""És um Auditor Financeiro Sénior especialista em contabilidade Portuguesa. A tua missão é responder com precisão cirúrgica, mas o teu objetivo é ser útil e esclarecedor, não apenas um filtro de texto..

REGRAS DE OURO:
1. Usa EXCLUSIVAMENTE a informação fornecida na secção <contexto_financeiro>. 
2. Tem atenção redobrada: o contexto pode conter informações de vários municípios misturados. Foca-te APENAS no que é pedido na pergunta.
3. Se a resposta não estiver no contexto, sê honesto e diz que não há dados no excerto recuperado.

DIRETRIZES DE FORMATAÇÃO:
* Síntese: Responde logo à pergunta de forma direta.
* Tabela ou Bullet Points: Organiza a informação de forma visualmente apelativa usando bullets ou tabelas em Markdown. Usa emojis profissionais (🏛️, 📊, 📝, ...).
* Momento Didático: Adiciona uma breve secção final chamada "💡 Nota do Auditor:" onde dás um breve insight.

<contexto_financeiro>
{contexto}
</contexto_financeiro>

PERGUNTA EM ANÁLISE: 
{pergunta}

PARECER DO AUDITOR:"""

    resposta = llm.invoke([HumanMessage(content=prompt)])
    return resposta.content # Aqui mudamos: em vez de fazer print, a função devolve o texto!

# Criar a rota (API Endpoint) que o HTML vai chamar
@app.route('/perguntar', methods=['POST'])
def perguntar_api():
    dados = request.json
    pergunta_utilizador = dados.get('pergunta')
    
    if not pergunta_utilizador:
        return jsonify({"erro": "Pergunta não fornecida"}), 400

    print(f"\nA processar pergunta recebida da web: {pergunta_utilizador}")
    
    try:
        # Chama a tua função RAG
        resposta_final = executar_pergunta(pergunta_utilizador)
        # Devolve a resposta em formato JSON para a página web
        return jsonify({"resposta": resposta_final})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == "__main__":
    print("🚀 Servidor da API RAG iniciado na porta 5000...")
    app.run(port=5000, debug=True)