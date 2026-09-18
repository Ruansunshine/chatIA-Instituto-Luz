"""Modelos Pydantic (schemas de entrada/saida) usados pelas rotas do
FastAPI em main.py. Sao so estrutura de dados (validacao automatica do
corpo da requisicao), nenhuma logica aqui - fica junto pra main.py nao
ficar misturando rota com definicao de schema.
"""

from pydantic import BaseModel


class Troca(BaseModel):
    """Uma troca (pergunta + resposta) do historico da conversa, usada
    pra dar contexto de follow-up pro Ollama. Vem do front, que guarda o
    historico de sessao e reenvia a cada pergunta nova."""

    pergunta: str
    resposta: str


class PerguntaRequest(BaseModel):
    """Corpo esperado em POST /responder: a pergunta atual do usuario mais
    o historico de trocas anteriores da mesma sessao (pode vir vazio, ex:
    primeira pergunta da conversa)."""

    pergunta: str
    historico: list[Troca] = []
