"""Geracao da resposta: monta o prompt (system + contexto RAG + historico),
chama o Ollama local em streaming e devolve pedaco por pedaco pro chamador
(main.py so consome gerar_stream, sem saber desses detalhes). Tambem cuida
do aviso opcional de "Alto Desempenho" no Windows durante a geracao.
"""

import json
import logging

import httpx

from modules.config import MENSAGEM_TIMEOUT, OLLAMA_MODEL, OLLAMA_URL, POWER_BOOST_URL
from modules.modelos import Troca
from modules.regras import montar_system_prompt

logger = logging.getLogger("instituto-luz-ia")

# Constantes de geracao/timeout, afinadas na pratica (auditoria de bugs reais,
# ver documentacao/pbi/backend/us.md): read=None deixa a IA responder no tempo
# dela numa CPU sem GPU (quem corta de verdade e' o idleTimeout de 250s do
# Node, api/index.ts, se a conexao ficar ociosa - geracao lenta mas genuina
# nunca e' cortada); num_predict reduzido de 300 pra 200 porque RAG + resposta
# longa juntos estouravam o timeout (MENSAGEM_TIMEOUT, mostrada nesse caso,
# vem de modules/config.py).
TIMEOUT_OLLAMA = httpx.Timeout(connect=5.0, read=None, write=10.0, pool=5.0)
NUM_PREDICT_MAXIMO = 200


def montar_mensagens(pergunta: str, historico: list[Troca], contexto: str) -> list[dict]:
    mensagens = [{"role": "system", "content": montar_system_prompt()}]
    if contexto:
        mensagens.append(
            {
                "role": "system",
                "content": (
                    "Use as informacoes abaixo, extraidas dos documentos oficiais "
                    "da clinica, pra responder com precisao. Se a resposta nao "
                    "estiver aqui, diga que nao tem certeza e sugira contato com "
                    f"a recepcao:\n\n{contexto}"
                ),
            }
        )
    for troca in historico:
        mensagens.append({"role": "user", "content": troca.pergunta})
        mensagens.append({"role": "assistant", "content": troca.resposta})
    mensagens.append({"role": "user", "content": pergunta})
    return mensagens


async def _avisar_power_boost(ligar: bool) -> None:
    caminho = "/ligar" if ligar else "/desligar"
    try:
        async with httpx.AsyncClient(timeout=0.5) as client:
            # Header Host forcado pra "localhost" - o HttpListener do
            # PowerShell (power-boost-listener.ps1) so aceita esse prefixo
            # sem exigir rodar como Administrador; sem isso, o Windows
            # rejeita (400) a chamada vinda de host.docker.internal.
            await client.get(
                f"{POWER_BOOST_URL}{caminho}", headers={"Host": "localhost"}
            )
    except Exception:
        # Listener nao esta rodando, ou host.docker.internal nao resolveu -
        # nao e' erro de verdade, e' o caso normal quando ninguem ligou o
        # boost manual. Nunca deve atrapalhar a resposta da IA.
        pass


async def gerar_stream(pergunta: str, historico: list[Troca], contexto: str):
    # O "desligar" no finally roda SEMPRE - sucesso, timeout ou erro - senao
    # uma falha no meio da geracao deixa o Windows preso no Alto Desempenho
    # pra sempre (o proprio power-boost-listener.ps1 tambem desliga sozinho
    # se essa janela for fechada, como segunda rede de seguranca).
    await _avisar_power_boost(ligar=True)
    try:
        try:
            async with httpx.AsyncClient(timeout=TIMEOUT_OLLAMA) as client:
                async with client.stream(
                    "POST",
                    f"{OLLAMA_URL}/api/chat",
                    json={
                        "model": OLLAMA_MODEL,
                        "messages": montar_mensagens(pergunta, historico, contexto),
                        "stream": True,
                        "options": {"num_predict": NUM_PREDICT_MAXIMO},
                        # Sem isso o Ollama descarrega o modelo da RAM apos um
                        # tempo curto de ociosidade - a proxima pergunta paga de
                        # novo o custo de carregar 2.6GB do disco (~28s medidos
                        # na pratica). Mantendo carregado, esse custo some na
                        # maioria das perguntas (so paga na primeira).
                        "keep_alive": "30m",
                    },
                ) as resposta:
                    resposta.raise_for_status()
                    async for linha in resposta.aiter_lines():
                        if not linha:
                            continue
                        try:
                            dados_linha = json.loads(linha)
                        except json.JSONDecodeError:
                            # Uma linha malformada aqui derrubava o gerador
                            # inteiro silenciosamente (corpo vazio pro cliente,
                            # sem nenhum erro visivel) - agora so pula a linha.
                            logger.warning("Linha invalida do Ollama, ignorada: %r", linha[:200])
                            continue
                        pedaco = dados_linha.get("message", {}).get("content", "")
                        if pedaco:
                            yield pedaco
        except (httpx.TimeoutException, httpx.HTTPError):
            # O stream ja pode ter mandado pedaco pro cliente antes de travar -
            # a mensagem de timeout entra como continuacao, nao como um erro cru.
            yield f"\n\n{MENSAGEM_TIMEOUT}"
        except Exception:
            # Rede de seguranca final - qualquer erro nao previsto NAO pode
            # fechar o stream silenciosamente (foi o que aconteceu antes desse
            # fix: corpo 200 OK vazio, sem log nenhum, depois de dezenas de
            # segundos). Sempre loga e sempre avisa o usuario.
            logger.exception("Erro inesperado gerando resposta pro Ollama.")
            yield "\n\nDesculpe, ocorreu um erro inesperado aqui. Tente novamente."
    finally:
        await _avisar_power_boost(ligar=False)
