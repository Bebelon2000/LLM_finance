import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

# 1. Configurações de Supressão de Avisos (Melhora a leitura do log)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
logging.basicConfig(level=logging.WARNING)

# ⚠️ Lembra-te de usar variáveis de ambiente em produção
os.environ["GOOGLE_API_KEY"] = "AIzaSyDPiz7ikditkr4DS8xcu81e6UielcaKtIg"

# ==========================================
# INICIALIZAÇÃO GLOBAL (O SEGREDO DA VELOCIDADE)
# ==========================================
# Carregamos os modelos APENAS UMA VEZ quando o servidor liga
print("🧠 A carregar modelos e base de dados... Por favor, aguarda.")

embeddings = HuggingFaceEmbeddings(
    model_name="intfloat/multilingual-e5-large",
    model_kwargs={'device': 'cpu'} # Se tiveres GPU, muda para 'cuda'
)

caminho_bd = r"C:\Users\berna\RAG_livro_ORDEM_CONTABILISTAS\bd_vetorial"
vector_db = Chroma(
    persist_directory=caminho_bd, 
    embedding_function=embeddings, 
    collection_name="contabilidade_portuguesa"
)

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.1)
print("✅ Sistema pronto para receber perguntas!")

app = Flask(__name__)
CORS(app)

def pesquisar_contexto(pergunta):
    # A pesquisa agora é instantânea pois o vector_db já está na memória
    resultados = vector_db.similarity_search(pergunta, k=8)
    return "\n\n".join([doc.page_content for doc in resultados])

def executar_pergunta(pergunta):
    contexto = pesquisar_contexto(pergunta)

    # Prompt Otimizado (Versão 2.0 - Menos restrito e mais analítico)
    prompt = f"""És um Auditor Financeiro Sénior e Consultor Técnico especialista em SNC-AP e POCAL. 
A tua missão é responder com precisão cirúrgica e rigor técnico.

HIERARQUIA DE RESPOSTA:
1. Se a pergunta for sobre dados de municípios ou anos, usa o <contexto_financeiro>.
2. Se a pergunta for uma definição teórica (ex: "O que é..."), usa o teu conhecimento para explicar com clareza.
3. Se os dados não estiverem presentes, indica que a informação não consta mas sugere onde pode ser encontrada.

DIRETRIZES:
* Responde de forma direta no topo.
* Usa Tabelas Markdown ou Bullet Points para dados numéricos.
* Termina sempre com a secção "💡 Nota do Auditor:".

<contexto_financeiro>
{contexto}
</contexto_financeiro>

PERGUNTA: {pergunta}

PARECER DO AUDITOR:"""

    resposta = llm.invoke([HumanMessage(content=prompt)])
    return resposta.content

@app.route('/perguntar', methods=['POST'])
def perguntar_api():
    dados = request.json
    pergunta_utilizador = dados.get('pergunta')
    
    if not pergunta_utilizador:
        return jsonify({"erro": "ão fornecPergunta nida"}), 400

    try:
        resposta_final = executar_pergunta(pergunta_utilizador)
        return jsonify({"resposta": resposta_final})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5000, debug=False) # debug=False evita recarregar o modelo duas vezes