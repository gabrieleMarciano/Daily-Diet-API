# Base Python
FROM python:3.11-slim

# Define diretório de trabalho
WORKDIR /app

# Copia apenas o requirements para instalar dependências
COPY requirements.txt .

# Instala dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código
COPY . .

# Variáveis de ambiente
ENV FLASK_APP=app:create_app
ENV FLASK_ENV=development

# CMD para rodar Flask com recarga automática
CMD ["flask", "run", "--host=0.0.0.0", "--reload"]


