# Usa uma imagem oficial do Python, versão slim para ser mais leve
FROM python:3.10-slim

# Define o diretório de trabalho dentro do contentor
WORKDIR /app

# Copia o ficheiro de dependências primeiro (otimiza o cache do Docker)
COPY requirements.txt .

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o resto do teu projeto para dentro do contentor
COPY . .

# Expõe a porta 5000
EXPOSE 5000

# Comando para iniciar o servidor
CMD ["python", "app.py"]