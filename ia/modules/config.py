"""Configuracao lida do ambiente (variaveis injetadas pelo docker-compose) e
mensagens fixas de texto usadas em main.py. Sem logica nem tuning de
comportamento - constantes que mudam O QUE a IA usa/mostra (ver main.py pras
constantes que mudam COMO ela se comporta, essas ficam coladas na funcao
que elas afetam, com o motivo do valor escolhido).
"""

import os

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")

# Host onde roda o power-boost-listener.ps1 (chat/power-boost-listener.ps1)
# - fora do Docker, direto no Windows. Puramente opcional: se a janela do
# script nao estiver aberta, essas chamadas falham rapido (timeout curto) e
# sao ignoradas em silencio - o chat continua normal, so sem o boost de CPU.
# host.docker.internal e' o endereco que o Docker Desktop da pro container
# alcancar o host Windows.
POWER_BOOST_URL = os.getenv("POWER_BOOST_URL", "http://host.docker.internal:5959")

# Mostrada pro usuario quando o Ollama trava/nao responde a tempo (ver
# gerar_stream em main.py).
MENSAGEM_TIMEOUT = (
    "Desculpe, o assistente demorou demais pra responder. Tente novamente "
    "ou reformule a pergunta de um jeito mais direto."
)
