# Checklist de Entrega — Trabalho Prático (Sistemas Inteligentes)

Confere o que foi pedido no enunciado (post do prof. Edilson Carlos Silva Lima, 28/08/2026, ver [`requisito.md`](./requisito.md) para o texto oficial arquivado) contra o que o projeto `chat/` entrega hoje. Cada item foi checado direto no código/config, não é achismo.

## O mínimo exigido

| Exigência do enunciado | Status | Onde |
|---|---|---|
| Chat de IA que interage e extrai informação dos documentos fornecidos | ✅ | `POST /chat` (`api/index.ts`) → `POST /responder` (`ia/main.py`) |
| Processar/recuperar informação de **PDF** | ✅ | `ia/modules/rag.py` (`gerar_chunks_pdf`), fonte `ia/dados/guia_do_paciente.pdf` |
| Processar/recuperar informação de **XLSX** | ✅ | `ia/modules/rag.py` (`gerar_chunks_planilha`), fonte `ia/dados/precos_profissionais.xlsx` |
| Processar/recuperar informação de **MySQL** | ✅ | `GET /disponibilidade` consulta direto (`api/src/db/queries.ts`), sem passar pela IA |
| MongoDB (opcional) | ⬜ não feito | Fora de escopo por decisão do grupo — o enunciado marca como opcional |
| Proibido API paga/externa (OpenAI, Anthropic etc.) na versão final | ✅ | Só Ollama local (`qwen2.5:3b`), ver `ia/modules/config.py` + `docker-compose.yml` |
| API local própria (framework) | ✅ | FastAPI (Python) + Elysia/Bun (Node) |
| Liberdade de linguagem/ecossistema (front não precisa ser o React de exemplo) | ✅ | Front próprio em HTML/CSS/JS puro (`frontend/e2e.html`), decisão registrada no `README.md` |
| `README.md` com descrição do projeto | ✅ | `README.md` raiz, seção "Descrição do Projeto" |
| `README.md` com tecnologias utilizadas | ✅ | `README.md` raiz, seção "Tecnologias Utilizadas" (tabela) |
| `README.md` com guia de execução passo a passo (dependências, API local, banco, front) | ✅ | `README.md` raiz, seção "Guia de Execução (Passo a Passo)" |
| Repositório no GitHub/GitLab | ⬜ pendente | Ainda não publicado |
| Rodar numa dupla/individual, sem apresentação de slides | — | Formato de entrega, não é código |
| Apresentar funcionando ao professor no laboratório | ⬜ pendente | Data confirmada: 18/09/2026 (adiado do prazo original 11/09) |

## Além do mínimo pedido

Coisas que não eram exigidas e foram feitas mesmo assim:

- **Dois servidores de backend, cada um falando com um banco diferente**: o Node (`api/`) consulta direto o banco relacional (MySQL) pra disponibilidade e histórico; o Python (`ia/`) consulta o banco vetorial (ChromaDB) pra busca semântica no RAG. O enunciado só pede "uma API local própria" (singular) — separar em dois serviços, um por tipo de dado, é decisão de arquitetura do grupo, não exigência.
- **Banco vetorial (ChromaDB) pra RAG de verdade**: o enunciado cita só PDF/XLSX/MySQL como obrigatórios e MongoDB como opcional — em nenhum momento fala de banco vetorial ou busca semântica. Indexar os documentos em embeddings e buscar por similaridade (em vez de, por exemplo, jogar o texto inteiro do PDF/planilha no prompt) é diferencial técnico do grupo, não pedido no post.
- **Stack inteira dockerizada com um único comando** (`docker compose up -d --build`): MySQL, Flyway (migração automática), Ollama (com pull automático do modelo), ChromaDB, backend Node, backend Python e frontend sobem juntos, sem nenhum passo manual — o enunciado só pedia "instruções claras de como instalar/rodar", não que fosse um comando só.
- **Resposta em streaming** (token a token, `text/plain` com `X-Fontes` no header) em vez de esperar a resposta inteira pra devolver — melhor percepção de velocidade numa CPU sem GPU.
- **Memória de conversa por sessão**: histórico salvo no MySQL (`conversas`, `V2`/`V3` em `api/db/migration/`) e reinjetado no prompt do Ollama, permite pergunta de acompanhamento tipo "e o preço da segunda?" sem repetir contexto.
- **Busca "pega tudo" pra pergunta agregada**: perguntas como "quais especialidades" ou "quanto custa" buscam **todos** os chunks daquela categoria em vez de só os top-k por similaridade — evita o modelo contar/listar errado (`ia/modules/rag.py`, `buscar_todos_por_tipo`, ver `ia/main.py`).
- **Controle de concorrência da IA**: só uma pergunta de IA processa por vez; uma segunda pergunta recebe erro 429 claro em vez de esperar escondida numa fila (`api/src/modules/ia-stream.ts`).
- **Rede de segurança de timeout em duas camadas** (Python sem teto de leitura + idleTimeout de 250s no Node) pra geração longa numa CPU sem GPU nunca ser cortada no meio, só travamento de verdade é.
- **Suporte opcional a GPU NVIDIA**: `docker-compose.gpu.yml` + `start.ps1`/`start.sh` detectam GPU e aceleram automaticamente, caindo pro modo CPU se não tiver.
- **Endpoints de saúde** (`/health`, `/health/python`) pra diagnosticar rápido se algum serviço caiu, incluindo checagem de conexão real com o MySQL.
- **Documentação de processo além do README**: `escopo.md`, `backlog.md` (9 user stories), `documentacao/pbi/backend/us.md` (11 PBIs detalhados, com changelog de bugs reais encontrados e corrigidos numa auditoria), `testes_tempo_resposta.md` (bateria de perguntas cronometradas).
- **Código modularizado nos dois lados**: `ia/modules/` (config, modelos, rag, regras, criterio, geracao) e `api/src/modules/` (config, ia-stream) — os arquivos de entrada (`main.py`, `index.ts`) ficam só com rotas.
- **Cabeçalhos de segurança básicos** (`X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`) mesmo sem exigência do enunciado.

## Pendências antes da entrega final

1. Publicar o repositório no GitHub/GitLab.
2. Confirmar ao vivo que `docker compose up -d --build` funciona numa máquina limpa antes da apresentação (ver US09 em `backlog.md`).
