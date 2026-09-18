Aqui estão referentes as atividades do backend, tanto node quanto a ia em python

> Ver [`../../escopo.md`](../../escopo.md) (arquitetura), [`../../requisito.md`](../../requisito.md) (enunciado oficial) e [`../../backlog.md`](../../backlog.md) (visão geral de todas as USs, front incluído). Este arquivo detalha só a parte de backend (Node + serviço Python) em tarefas menores, prontas pra codar.

Dado-fonte já gerado e validado em `chat/ia/dados/`: `guia_do_paciente.pdf`, `precos_profissionais.xlsx`, `V1__cria_grade_disponibilidade.sql` (rodado de verdade num MySQL 8 descartável, sem erro).

## Status real em 17/09/2026 — todos os blocos (B01-B11) implementados e testados

**Tudo funcionando ponta a ponta**: front (`e2e.html`) → Node (`/chat`, streaming) → decide disponibilidade (MySQL direto) vs IA (Python `/responder`, streaming) → Python faz RAG real (Chroma) → Ollama gera com contexto real → resposta volta em streaming, com fonte real no header `X-Fontes`, logada em `conversas` (com `session_id`, histórico de sessão incluído no prompt pra follow-up funcionar).

**Desvios do plano original abaixo** (documentados pra quem for mexer depois):
- **PBI-B06 mudou de abordagem**: nada de chunking por heading (`##`) hardcoded — isso "entregava o conteúdo pronto" pro código em vez do sistema ler o PDF de verdade (feedback direto do usuário). Chunking é **genérico, por janela de caracteres** (`TAMANHO_CHUNK=800`, overlap 150), funciona em qualquer PDF, ver `chat/ia/modules/rag.py`.
- **PBI-B10 mudou de formato**: não é `{ resposta, fontes }` em JSON — é **streaming de texto puro** (`StreamingResponse`, `text/plain`), com fontes num header `X-Fontes` separado. Decisão pra dar sensação de resposta em tempo real (pedido explícito do usuário).
- Regras de comportamento do modelo viraram dois arquivos: `chat/ia/modules/regras.py` (SYSTEM_PROMPT + funções determinísticas — cumprimento por horário, filtro de palavrão) e `chat/ia/modules/criterio.py` (só o critério de quando algo é prompt vs código, catálogo de decisões).

**Bugs reais encontrados e corrigidos numa sessão de auditoria (madrugada de 17/09)**, guardar como conhecimento pra não repetir:
1. **`chromadb` client incompatível com a versão do servidor** (`:latest` do Chroma tinha subido pra 1.0, client Python pinado em 0.6.3) — corrigido pinando as duas versões junto (`chromadb==1.0.15` + imagem `chromadb/chroma:1.0.0`, não usar `:latest` de novo).
2. **Alucinação de preço real**: `top_k=2` na busca do Chroma deixava de fora o chunk certo de preço (ficava em 3º lugar no ranking de similaridade) — modelo respondeu R$ 420 quando o valor real era R$ 612. Corrigido subindo pra `top_k=4`. Lição: correção de valor pro paciente pesa mais que alguns segundos a mais de resposta.
3. **JSON malformado no stream do Ollama derrubava o gerador Python silenciosamente** (corpo `200 OK` vazio, sem log nenhum) — `except` só cobria erro de `httpx`, não `JSONDecodeError`. Corrigido com try/except por linha + catch-all no gerador + `logging.basicConfig` (os logs nunca apareciam porque logging não estava configurado).
4. **Vazamento de conexão no client do Chroma** — `chromadb.HttpClient()` era recriado a cada chamada, sem fechar o anterior (achado via `/proc/net/tcp` no container: 10 conexões ESTABLISHED ociosas). Corrigido com client singleton em `modules/rag.py`.
5. **Causa raiz da "demora infinita"/corpo vazio no Node**: `idleTimeout` padrão do `Bun.serve()` matava a conexão HTTP no meio do streaming, antes da IA terminar (respostas legítimas de 40-60s+ excediam o limite padrão). Corrigido com `app.listen({ ..., idleTimeout: 120 })` em `chat/api/index.ts`. Esse foi o bug mais difícil de achar — só apareceu auditando com logs de debug temporários dentro do `pull()` do `ReadableStream`.
6. **Falha real de resiliência**: `buscar_contexto` (busca no Chroma) não tinha timeout nenhum — corrigido com `asyncio.wait_for(..., timeout=15.0)` em `main.py`.

**Não confiar cegamente em teste isolado**: um bug (idleTimeout) só aparecia no caminho completo Node→Python→Ollama, nunca testando Python isolado (`curl localhost:8001/responder` direto sempre funcionou). Testar sempre pelo caminho real (`localhost:4000/chat`) antes de dar algo como resolvido.

## Stack proposta

- **Node**: Bun + Elysia + Drizzle ORM + MySQL — mesma stack do SmartClinic real, escolhida por familiaridade (acelera o desenvolvimento, dentro do prazo apertado). Liberdade total pelo enunciado, mas sem motivo pra trocar.
- **Python**: FastAPI (simples, assíncrono, boa integração com ChromaDB e requests HTTP pro Ollama) + `chromadb` + `ollama` (client Python) + `pypdf`/`openpyxl` pra ingestão.
- **Comunicação Node ↔ Python**: HTTP simples (`fetch`/`httpx`), sem WebSocket/streaming (SSE é bônus, só se sobrar tempo — ver `escopo.md`).

Se você quiser trocar (ex: Express puro em vez de Elysia), só avisar — isso muda a estrutura de pastas abaixo.

---

## Bloco 1 — Node: fundação

### PBI-B01 — Setup do projeto Node
- Inicializar projeto Bun (`bun init`) em `chat/api/`.
- Instalar Elysia, Drizzle ORM, driver MySQL (`mysql2`).
- Estrutura mínima: `src/index.ts` (entrypoint Elysia), `src/db/schema.ts` (Drizzle schema espelhando as 3 tabelas da migração Flyway), `src/db/client.ts` (conexão).
- `.env.example` com `DATABASE_URL`, porta da API, URL do serviço Python.

### PBI-B02 — Migração Flyway + schema Drizzle
- Copiar `chat/ia/dados/V1__cria_grade_disponibilidade.sql` pra `chat/api/db/migration/` (convenção Flyway: `V1__descricao.sql`).
- Rodar Flyway no startup do container (ou via script local `flyway migrate` pra desenvolvimento).
- Escrever o schema Drizzle (`especialidades`, `profissionais`, `disponibilidade`) batendo exatamente com as colunas da migração.
- Critério de aceite: `bun run` local conecta no MySQL, schema Drizzle reflete a tabela real (testar com uma query simples).

### PBI-B03 — `GET /health`
- Retorna `{ status: "ok", db: "connected" | "error" }`.
- Critério de aceite: container do backend-node só é considerado "healthy" no docker-compose depois que esse endpoint responde 200 (healthcheck).

### PBI-B04 — `GET /disponibilidade`
- Query direta no MySQL via Drizzle: join `disponibilidade` + `profissionais` + `especialidades`.
- Filtros opcionais por query string: `?especialidade=` e/ou `?profissional=`.
- Resposta JSON: lista de `{ profissional, especialidade, dia_semana, horario_inicio, horario_fim }`.
- Sem auth (decisão do escopo).

## Bloco 2 — Python: ingestão (RAG - indexação)

### PBI-B05 — Setup do serviço Python
- Projeto FastAPI em `chat/ia/`.
- `requirements.txt`: `fastapi`, `uvicorn`, `chromadb`, `ollama`, `pypdf`, `openpyxl`, `pandas`.
- `main.py` com endpoint `GET /health`.

### PBI-B06 — Ingestão do PDF
- Ler `guia_do_paciente.pdf` (usar `pypdf` pra extrair texto).
- Chunking por seção (usar os headings `##` como separador natural — o PDF já foi gerado com heading por seção, ver `chat/ia/dados/guia_do_paciente.pdf`).
- Gerar embedding de cada chunk e gravar no ChromaDB, com metadado `{ fonte: "guia_do_paciente.pdf", secao: <nome da seção> }`.

### PBI-B07 — Ingestão da planilha
- Ler `precos_profissionais.xlsx` (usar `openpyxl`/`pandas`, as duas abas: `Precos_Pacotes` e `Profissionais_Horarios`).
- Transformar cada linha (ou grupo de linhas por especialidade) num texto legível antes de gerar embedding (ex: "Pilates, pacote de 4 sessões: R$ 324,00, válido por 60 dias").
- Gravar no Chroma com metadado `{ fonte: "precos_profissionais.xlsx", aba: <nome da aba> }`.

### PBI-B08 — Orquestração da ingestão no startup
- Script `ingest.py` (ou rota interna chamada uma vez no boot) que roda PBI-B06 + PBI-B07.
- Idempotente: antes de inserir, limpar a coleção do Chroma (ou checar se já tem os mesmos documentos) — não pode duplicar chunk a cada restart do container.
- Log claro de quantos chunks foram indexados por fonte.

## Bloco 3 — Python: geração (RAG - resposta)

### PBI-B09 — Pull automático do modelo Ollama
- Configurar no `docker-compose` (ou num script de init) o pull automático do modelo (`llama3.2:3b` ou `qwen2.5:3b`) na subida do container `ollama`.
- Critério de aceite: `docker compose up -d --build` numa máquina limpa já deixa o modelo baixado, sem passo manual.

### PBI-B10 — `POST /responder` (endpoint interno, chamado pelo Node)
- Recebe `{ pergunta: string }`.
- Busca top-k chunks relevantes no Chroma.
- Monta prompt (pergunta + contexto recuperado, instrução pro modelo citar a fonte).
- Chama Ollama local, devolve `{ resposta: string, fontes: string[] }`.
- Testar manualmente com pelo menos 5 perguntas cobrindo especialidades, políticas e preços (disponibilidade não passa por aqui — vai direto no Node, PBI-B04).

## Bloco 4 — Node: orquestração do chat

### PBI-B11 — `POST /chat`
- Recebe `{ pergunta: string }`.
- Heurística simples pra decidir a rota: se a pergunta contém palavras-chave de disponibilidade/horário/agenda → resolve direto via PBI-B04 (MySQL). Caso contrário → repassa pro `POST /responder` do serviço Python (PBI-B10).
- Resposta unificada pro front, independente da rota: `{ resposta: string, fontes: string[] }`.
- Tratar timeout/erro do serviço Python com mensagem amigável (não estourar 500 cru pro paciente).

---

## Ordem sugerida
PBI-B01 → B02 → B03 → B04 (Node de pé e testável isoladamente) → B05 → B06 → B07 → B08 (ingestão Python funcionando, verificável direto no Chroma) → B09 → B10 (geração funcionando isolada, testar via curl direto no Python) → B11 (integração final Node ↔ Python).

Cada bloco pode ser testado sem depender do frontend (US06/US07 do `backlog.md`) — usar `curl`/Postman/Insomnia pra validar antes do front existir.
