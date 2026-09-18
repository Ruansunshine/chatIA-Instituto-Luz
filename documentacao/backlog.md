# Backlog — Assistente Virtual do Instituto Luz (chat pra pacientes)

> Ver [`escopo.md`](./escopo.md) (arquitetura/decisões) e [`requisito.md`](./requisito.md) (enunciado oficial) antes de começar qualquer item.

Convenção: cada PBI é uma US (user story) com critério de aceite objetivo. Ordem sugerida de execução é a ordem da lista — cada bloco depende do anterior.

---

## US01 — Infra: docker-compose base
**Como** desenvolvedor, **quero** um `docker-compose.yml` único que suba toda a stack, **para** não precisar de passo manual.

Critério de aceite:
- Serviços: `mysql`, `ollama` (com pull automático do modelo no start), `chroma`, `backend-node`, `backend-python`, `frontend`.
- `docker compose up -d --build` sobe tudo do zero e a ingestão de PDF/XLSX roda sozinha (depende de US04).
- `GET /health` do backend-node responde 200 só depois que MySQL + Flyway estão prontos (depende de US02).

## US02 — Backend Node: schema + migração + disponibilidade
**Como** paciente (via chat), **quero** consultar a disponibilidade real de horário, **para** saber quando posso agendar.

Critério de aceite:
- Drizzle ORM conectado ao MySQL; schema versionado via Flyway usando `chat/ia/dados/V1__cria_grade_disponibilidade.sql` (já gerado e validado).
- `GET /disponibilidade` — consulta direta no MySQL (especialidade/profissional/dia/horário), sem passar pelo Python/Ollama.
- `GET /health` — retorna status da API + conexão com MySQL.
- API enxuta, sem módulos, sem auth (conforme `escopo.md`).

## US03 — Backend Node: endpoint de chat (orquestração)
**Como** paciente, **quero** perguntar qualquer coisa num único endpoint de chat, **para** não precisar saber se a resposta vem do banco ou da IA.

Critério de aceite:
- `POST /chat` recebe `{ pergunta: string }`.
- Se a pergunta for sobre disponibilidade/horário (heurística simples ou palavra-chave), resolve direto no MySQL.
- Caso contrário, repassa pro serviço Python (`POST` interno) e devolve a resposta + fonte.
- Comunicação Node ↔ Python via HTTP simples (sem WebSocket/streaming — SSE é bônus, só se sobrar tempo).

## US04 — Serviço Python: ingestão automática (RAG - indexação)
**Como** sistema, **quero** processar o PDF e a planilha automaticamente no startup, **para** a base de conhecimento estar pronta assim que o chat abrir.

Critério de aceite:
- No start do container, lê `guia_do_paciente.pdf` e `precos_profissionais.xlsx` (de `chat/ia/dados/`, copiados pro container).
- Chunking do texto (por seção do PDF, por linha/aba da planilha) → embedding → grava no ChromaDB.
- Idempotente: rodar de novo não duplica os chunks (limpa a coleção ou verifica se já foi ingerido).
- Log claro de sucesso/erro da ingestão (útil pra debugar na apresentação ao professor).

## US05 — Serviço Python: endpoint de resposta (RAG - geração)
**Como** paciente, **quero** receber uma resposta certeira citando a fonte, **para** confiar no que o chat disse.

Critério de aceite:
- Endpoint HTTP interno (chamado pelo backend-node) recebe a pergunta.
- Busca os chunks mais relevantes no Chroma (top-k).
- Monta o prompt (pergunta + contexto recuperado) e chama o Ollama local (llama3.2:3b ou qwen2.5:3b).
- Resposta inclui o texto gerado + referência da fonte (ex: "Guia do Paciente, seção Política de Cancelamento" ou "planilha de preços, aba Precos_Pacotes").
- Testar manualmente com pelo menos 5 perguntas cobrindo as 4 áreas do escopo funcional (especialidades, políticas, preços, disponibilidade).

## US06 — Frontend: tela de chat
**Como** paciente, **quero** uma interface simples de pergunta/resposta, **para** tirar minha dúvida sem falar com a recepção.

Critério de aceite:
- React, front próprio (não reaproveita o esqueleto do `tde-ia.zip` — decisão já tomada).
- Campo de pergunta + histórico da conversa na tela + indicação visual da fonte quando houver.
- Chama `POST /chat` do backend-node.
- Estado de loading enquanto aguarda resposta (a geração local via Ollama pode demorar alguns segundos).

## US07 — Frontend: aba "Documentos"
**Como** professor (avaliador), **quero** ver os documentos-fonte, **para** comparar a resposta do chat com o conteúdo original.

Critério de aceite:
- Aba/tela separada listando `guia_do_paciente.pdf` e `precos_profissionais.xlsx`, com link pra abrir/baixar cada um.
- Arquivos servidos como estáticos (sem endpoint novo além de expor os arquivos).

## US08 — README.md do repositório
**Como** professor (avaliador), **quero** um passo a passo claro, **para** rodar o projeto sem ajuda de ninguém.

Critério de aceite (exigência literal do enunciado — ver `requisito.md`):
- Descrição do projeto (escopo e o que a solução faz).
- Tecnologias utilizadas (todas as ferramentas, linguagens e bibliotecas).
- Guia de execução passo a passo: instalar dependências, rodar a API local, subir o banco de dados, executar o front-end.
- Testado por alguém que nunca viu o projeto antes (ou pelo menos lido em voz alta imaginando isso).

## US09 — Roteiro de validação ao vivo
**Como** dupla, **quero** um roteiro do que mostrar na apresentação, **para** não travar na hora H.

Critério de aceite:
- Lista de 5-8 perguntas de demonstração cobrindo especialidades, políticas, preços e disponibilidade.
- Confirmar que `docker compose up -d --build` funciona numa máquina limpa (ou pelo menos numa segunda pasta/branch) antes da apresentação.
- Ter um plano B se o Ollama demorar demais pra gerar (modelo pequeno já é decisão pensando nisso).

---

**Fora do backlog por decisão explícita** (ver `escopo.md`): upload de documento ao vivo durante a avaliação, autenticação/RBAC, integração real com o SmartClinic, MongoDB (opcional, só se sobrar tempo depois de US01-US09).
