# Checklist de Entrega

Detalhes e evidências (onde cada item está no código) em [`documentacao/checklist_entrega.md`](./documentacao/checklist_entrega.md).

## Mínimo exigido pelo enunciado

- [x] Chat de IA que interage e extrai informação dos documentos fornecidos
- [x] Processa e recupera informação de **PDF**
- [x] Processa e recupera informação de **XLSX**
- [x] Processa e recupera informação de **MySQL**
- [ ] Integração opcional com **MongoDB** (não feito, é opcional)
- [x] Sem API paga/externa (OpenAI, Anthropic etc.) — só IA local (Ollama)
- [x] API local própria, usando framework
- [x] Liberdade de linguagem/ecossistema respeitada (front próprio, não o React de exemplo)
- [x] `README.md` com descrição do projeto
- [x] `README.md` com tecnologias utilizadas
- [x] `README.md` com guia de execução passo a passo
- [x] Repositório publicado no GitHub/GitLab (https://github.com/Ruansunshine/chatIA-Instituto-Luz)
- [ ] Apresentação funcionando ao professor no laboratório

## Além do mínimo

- [x] Dois servidores de backend (Node e Python), cada um falando com um banco diferente: o Node consulta direto o banco relacional (MySQL), o Python consulta o banco vetorial (ChromaDB) pra busca semântica — divisão de arquitetura não pedida pelo enunciado (que só exige "uma API local própria")
- [x] Banco vetorial (ChromaDB) pra RAG de verdade (busca semântica), o enunciado só cita PDF/XLSX/MySQL/MongoDB opcional, não menciona banco vetorial em nenhum momento
- [x] Stack inteira sobe com um único comando (`docker compose up -d --build`)
- [x] Resposta em streaming (token a token)
- [x] Memória de conversa por sessão (segue pergunta de acompanhamento)
- [x] Busca "pega tudo" pra pergunta agregada (evita contagem/lista errada)
- [x] Controle de concorrência da IA (uma pergunta por vez, erro claro na segunda)
- [x] Timeout em duas camadas (Python + idleTimeout do Node)
- [x] Suporte opcional a GPU NVIDIA (override + scripts de start)
- [x] Endpoints de saúde (`/health`, `/health/python`)
- [x] Documentação de processo (escopo, backlog, PBIs, testes de tempo de resposta)
- [x] Código modularizado nos dois backends (`modules/` no Node e no Python)
- [x] Cabeçalhos de segurança básicos (`X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`)
