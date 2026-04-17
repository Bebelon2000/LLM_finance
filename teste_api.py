import os
import google.generativeai as genai

# A tua chave
os.environ["GOOGLE_API_KEY"] = "AIzaSyDPiz7ikditkr4DS8xcu81e6UielcaKtIg"
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

print("🔍 A verificar modelos disponíveis para esta API Key...")
print("-" * 40)

try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"✅ Modelo suportado: {m.name}")
    print("-" * 40)
    print("Sucesso! Copia um dos nomes acima (sem o 'models/') e avisa-me.")
except Exception as e:
    print(f"❌ Erro de autenticação ou conexão: {e}")