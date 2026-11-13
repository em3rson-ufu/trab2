# Imagem base enxuta, versão fixada (reprodutibilidade).
FROM python:3.12-slim

LABEL maintainer="<Émerson> <em3rson@ufu.br>" \
      description="Trabalho 2 — Inventário OO com análise de risco linear"

# Variáveis de ambiente:
#   PYTHONUNBUFFERED=1        → logs imediatos em docker logs.
#   PYTHONDONTWRITEBYTECODE=1 → não cria __pycache__ na imagem.
#   PYTHONPATH=/trab2           → encontra os pacotes dominio/, etc.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/trab2

WORKDIR /trab2

# Instala dependências primeiro (aproveita cache do Docker).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código (o .dockerignore evita lixo).
COPY . .

EXPOSE 5000

# Cria usuário sem privilégios (segurança).
RUN useradd --create-home --shell /bin/bash appuser \
 && mkdir -p /trab2/dados \
 && chown -R appuser:appuser /trab2
USER appuser

# Healthcheck: valida a aplicação a cada 30s.
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python main.py --relatorio > /dev/null 2>&1 || exit 1

CMD ["python", "main.py"]