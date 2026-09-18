import asyncio
import logging

from fastapi import FastAPI
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import StreamingResponse

from modules.geracao import gerar_stream
from modules.modelos import PerguntaRequest
from modules.rag import (
    buscar_contexto,
    buscar_todos_por_tipo,
    formatar_fontes,
    ingerir,
    montar_texto_contexto,
)
from modules.regras import (
    RESPOSTA_BLOQUEIO,
    contem_conteudo_bloqueado,
    eh_apenas_saudacao,
    resposta_saudacao,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("instituto-luz-ia")

app = FastAPI(
    title="Instituto Luz - Servico Python (IA)",
    version="0.1.0",
    description="Servico de RAG (ingestao + geracao) do trabalho de Sistemas Inteligentes.",
)


@app.on_event("startup")
async def ingerir_ao_iniciar():
    # Idempotente (ver modules/rag.py) - roda toda vez que o container sobe,
    # garante que `docker compose up` deixa tudo pronto sem passo manual.
    try:
        total = await run_in_threadpool(ingerir)
        logger.info("Ingestao concluida: %d chunks indexados no ChromaDB.", total)
    except Exception:
        logger.exception("Falha na ingestao no startup - Chroma pode estar indisponivel.")


@app.get("/")
def root():
    return {"success": True, "message": "Instituto Luz - Servico Python online"}


@app.get("/health")
def health():
    return {"success": True, "status": "ok", "service": "backend-python"}


@app.post("/responder")
async def responder(body: PerguntaRequest):
    if contem_conteudo_bloqueado(body.pergunta):

        async def bloqueio():
            yield RESPOSTA_BLOQUEIO

        return StreamingResponse(bloqueio(), media_type="text/plain; charset=utf-8")

    # Saudacao pura (bom dia/boa tarde/boa noite) nem chega a chamar o
    # Ollama - decidido em codigo com o horario real, mais rapido e
    # 100% confiavel (ver nota em modules/regras).
    if eh_apenas_saudacao(body.pergunta):

        async def saudacao():
            yield resposta_saudacao()

        return StreamingResponse(saudacao(), media_type="text/plain; charset=utf-8")

    # Pergunta AGREGADA ("quantos profissionais", "quais especialidades",
    # "quanto custa") precisa ver TODOS os chunks daquela categoria, nao so
    # os top_k mais parecidos - senao o modelo conta/lista errado (testado na
    # pratica: "quantos profissionais" nao achava dado suficiente e
    # desistia; "quais especialidades" listava so 1-3 de 7; pergunta de
    # preco direta as vezes trazia chunk do guia em vez da planilha de
    # precos, por busca por similaridade errar o alvo). Base e' pequena
    # (poucos chunks por tipo: preco e profissional), buscar tudo de uma
    # categoria e' barato (ver modules/rag.py). NAO fazer isso pro tipo
    # "guia" (PDF) - esse tem muito mais chunks, mandar tudo deixaria toda
    # pergunta lenta, nao so essas.
    pergunta_lower = body.pergunta.lower()
    tipo_agregado = None
    if any(p in pergunta_lower for p in ["quantos profissiona", "quais profissiona", "lista de profissiona", "todos os profissiona"]):
        tipo_agregado = "profissional"
    elif any(p in pergunta_lower for p in ["quais especialidad", "todas as especialidad", "lista de especialidad", "quantas especialidad"]):
        tipo_agregado = "preco"
    elif any(p in pergunta_lower for p in ["quanto custa", "qual o preco", "qual o valor", "valor do pacote", "preco do pacote", "precos e pacotes", "preco de um pacote", "quais os precos"]):
        tipo_agregado = "preco"

    try:
        if tipo_agregado:
            documentos, metadados = await asyncio.wait_for(
                run_in_threadpool(buscar_todos_por_tipo, tipo_agregado), timeout=15.0
            )
        else:
            # Timeout proprio - antes disso a busca no Chroma nao tinha
            # NENHUMA protecao contra travar, e um travamento aqui prendia a
            # request inteira antes mesmo de chegar no Ollama (que tem seu
            # timeout).
            documentos, metadados = await asyncio.wait_for(
                run_in_threadpool(buscar_contexto, body.pergunta), timeout=15.0
            )
    except Exception:
        logger.exception("Falha ao buscar contexto no ChromaDB - seguindo sem RAG.")
        documentos, metadados = [], []

    contexto = montar_texto_contexto(documentos)
    fontes = formatar_fontes(metadados)

    return StreamingResponse(
        gerar_stream(body.pergunta, body.historico, contexto),
        media_type="text/plain; charset=utf-8",
        headers={"X-Fontes": fontes} if fontes else None,
    )
