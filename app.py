import os
import logging
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
logging.basicConfig(level=logging.WARNING)

# A API Key será injetada pelo Docker (Variável de Ambiente)
google_api_key = os.getenv("GOOGLE_API_KEY")
if not google_api_key:
    raise ValueError("⚠️ ERRO: GOOGLE_API_KEY não foi definida nas variáveis de ambiente!")

print("🧠 A carregar modelos e base de dados... Por favor, aguarda.")

embeddings = HuggingFaceEmbeddings(
    model_name="intfloat/multilingual-e5-large",
    model_kwargs={'device': 'cpu'}
)

# Caminho relativo para funcionar dentro do Docker
caminho_bd = "./chroma_db_municipios"
vector_db = Chroma(
    persist_directory=caminho_bd, 
    embedding_function=embeddings, 
    collection_name="contabilidade_portuguesa"
)

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.1, google_api_key=google_api_key)
print("✅ Sistema pronto para receber perguntas!")

app = Flask(__name__)
CORS(app)

def pesquisar_contexto(pergunta):
    resultados = vector_db.similarity_search(pergunta, k=8)
    return "\n\n".join([doc.page_content for doc in resultados])

def executar_pergunta(pergunta):
    contexto = pesquisar_contexto(pergunta)
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

# Rota para servir o Frontend (HTML)
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/perguntar', methods=['POST'])
def perguntar_api():
    dados = request.json
    pergunta_utilizador = dados.get('pergunta')
    
    if not pergunta_utilizador:
        return jsonify({"erro": "Pergunta não fornecida"}), 400

    try:
        resposta_final = executar_pergunta(pergunta_utilizador)
        return jsonify({"resposta": resposta_final})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == "__main__":
    # host="0.0.0.0" é OBRIGATÓRIO no Docker para aceitar ligações externas
    app.run(host="0.0.0.0", port=5000, debug=False)