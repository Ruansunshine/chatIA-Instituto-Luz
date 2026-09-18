
Escopo — Assistente Virtual do Instituto Luz (chat pra pacientes)

> Ver [`requisito.md`](./requisito.md) para o enunciado oficial do trabalho (Sistemas Inteligentes, prof. Edilson) que este escopo atende.

Motivação: resolver a dependência da recepção pra tirar dúvida, dor real identificada na consultoria da clínica.

Objetivo: chat de IA generativa (RAG) que responde dúvidas institucionais do paciente, citando a fonte da resposta.

Escopo funcional:
- Especialidades oferecidas e o que cada uma trata
- Políticas de agendamento, cancelamento e falta
- Preços/pacotes de sessão
- Disponibilidade de horário por especialidade/profissional

Fora de escopo:
- Sem dado real de paciente (sem prontuário, CPF, histórico — tudo fictício)
- Não agenda de verdade, não integra com o SmartClinic real
- Não substitui orientação profissional/médica
- Sem autenticação/RBAC

Fontes de dados (do enunciado):
1. PDF — "Guia do Paciente" (texto institucional: especialidades, políticas)
2. XLSX — tabela de preços/pacotes + profissionais e horários
3. MySQL — grade de disponibilidade por especialidade/profissional (estruturado, fictício)
4. Mongo — fora por enquanto (opcional)

Restrição técnica: LLM 100% local via Ollama (modelo pequeno, llama3.2:3b ou qwen2.5:3b) — nada de API paga externa.

**Decisão final: `qwen2.5:3b`** (confirmado 17/09/2026, testado lado a lado com `llama3.2:3b` nas mesmas perguntas reais, mesmo pipeline): Qwen ficou ~20% mais rápido (44-47s vs 56-57s numa pergunta com RAG) **e** mais preciso (citou 3 de 7 especialidades reais vs 1 do Llama; Llama também deixou vazar o nome do documento-fonte dentro da resposta). Licença Apache 2.0 (mais permissiva que a licença própria da Meta pro Llama). Único deslize do Qwen: um erro pontual de concordância de gênero.

**Lentidão confirmada como 100% hardware, não arquitetura** (17/09/2026): mesmo código/pipeline testado numa segunda máquina com GPU dedicada (notebook, RTX 3050) via `docker-compose.gpu.yml` — resposta ficou visivelmente rápida (`ollama ps` mostrando uso de GPU, não CPU). Na máquina de desenvolvimento (Intel Iris Xe, GPU integrada, sem suporte no Ollama), a mesma pergunta leva 40-90s. Confirma que os ~40-90s no ambiente de dev são inteiramente explicados pela ausência de GPU dedicada, não por ineficiência do RAG/prompt.

Arquitetura:
- Front — React, chat simples (pergunta/resposta + fonte quando der) + aba/tela "Documentos" listando os arquivos-fonte (PDF do Guia do Paciente, planilha de preços) com link pra abrir/baixar — permite o professor comparar a resposta do chat com o documento original, reforça a citação de fonte
- Backend Node (Drizzle + MySQL, schema versionado via Flyway) — API enxuta, sem módulos, sem auth:
  - GET /disponibilidade — consulta direta no MySQL
  - POST /chat — recebe a pergunta, resolve direto (MySQL) ou repassa pro serviço Python, junta a resposta
  - GET /health
- Serviço Python — toda a IA: ingestão de PDF/XLSX → chunk → embedding → ChromaDB; na pergunta, busca no Chroma → monta prompt → chama Ollama → devolve resposta + fonte
- ChromaDB — vetor store pro conteúdo textual (PDF/XLSX)
- Comunicação Node ↔ Python: HTTP simples, sem WebSocket, sem streaming (SSE é bônus opcional, só se sobrar tempo)

Infra: tudo em docker-compose (mysql, ollama com pull automático do modelo, chroma, backend-node, backend-python, frontend) — docker compose up -d --build sobe tudo e roda a ingestão sozinho, sem passo manual.

**Decisão — ingestão fixa, não upload ao vivo (confirmado 16/09/2026):** os "documentos fornecidos" do enunciado são a base de conhecimento fixa (PDF + planilha), ingerida uma única vez no `docker-compose up`. O professor lê o PDF/planilha reais e faz perguntas sobre esse conteúdo já embedado — não há (e não é exigido) endpoint de upload ao vivo de novo arquivo durante a avaliação. Se sobrar tempo, upload dinâmico fica como possível bônus, não como requisito.

Prazo: sexta-feira, 18/09/2026.

~~Pendências antes de codar: conteúdo exato do PDF, da planilha e o schema do MySQL (dado fictício de disponibilidade).~~ **Resolvido em 16/09/2026** — gerados em `chat/ia/dados/`:
- `guia_do_paciente.pdf` — texto institucional completo (especialidades, políticas de agendamento/cancelamento/falta, FAQ), com elenco e especialidades reais do sistema SmartClinic.
- `precos_profissionais.xlsx` — abas `Precos_Pacotes` (35 linhas, 7 especialidades × 5 opções) e `Profissionais_Horarios` (7 profissionais reais, horário fictício).
- `V1__cria_grade_disponibilidade.sql` — migração Flyway (3 tabelas: especialidades, profissionais, disponibilidade), validada rodando de verdade num MySQL 8 descartável via Docker (22 linhas de disponibilidade, joins conferidos).

Elenco de profissionais é real (extraído do banco do sistema SmartClinic em 16/09/2026); preços e grade de horário são fictícios (não existem no sistema real).

---

Já salvei isso na minha memória do projeto SmartClinic. Se você quer levar isso pro diretório novo de um jeito que sobreviva independente da conversa, me fala o caminho da pasta que você vai abrir que eu já escrevo esse escopo direto num README.md/SCOPE.md lá dentro antes de você trocar de sessão.