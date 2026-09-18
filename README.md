# Instituto Luz: Chat de Base de Conhecimento com IA Generativa

Trabalho prático da disciplina de Sistemas Inteligentes (prof. Edilson Carlos Silva Lima), chatbot com IA generativa local (RAG) que responde perguntas de pacientes usando documentos reais de uma clínica de fisioterapia.

## Descrição do Projeto

O sistema é um assistente virtual que responde perguntas sobre a clínica (especialidades, preços, políticas, disponibilidade de horário) combinando três fontes de dados diferentes:

- **PDF** (`ia/dados/guia_do_paciente.pdf`): guia do paciente, processado por chunking genérico (sem cabeçalhos fixos, funciona com qualquer PDF) e indexado num banco vetorial.
- **XLSX** (`ia/dados/precos_profissionais.xlsx`): planilha de preços e profissionais, com duas abas, também indexada.
- **MySQL**: grade de disponibilidade de horário por profissional/especialidade, consultada **direto no banco**, sem passar pela IA (é dado estruturado, não precisa de busca semântica).

O fluxo geral de uma pergunta:

1. O **Node** decide se a pergunta é sobre disponibilidade (atalho direto no MySQL, sem IA) ou se precisa da IA.
2. Se precisa da IA, o **Python** busca o contexto mais relevante no **ChromaDB** (banco vetorial): busca semântica pra perguntas normais, busca por categoria inteira pra perguntas agregadas ("quantos profissionais", "quais especialidades").
3. O contexto encontrado é injetado num prompt e mandado pro **Ollama** (modelo `qwen2.5:3b`, rodando 100% local), que gera a resposta em streaming.
4. A conversa fica salva no MySQL por sessão, com memória das últimas trocas (segue perguntas de acompanhamento).

Não há nenhuma resposta hardcoded para perguntas sobre o conteúdo dos documentos: tudo que é fato (preço, especialidade, profissional) vem de ingestão real do PDF/XLSX, nunca de texto fixo no código.

## Tecnologias Utilizadas

| Camada | Tecnologia |
|---|---|
| LLM local | [Ollama](https://ollama.com/) + `qwen2.5:3b` (quantizado Q4_K_M, 100% local, sem API paga) |
| Banco vetorial (RAG) | ChromaDB |
| Backend de IA | Python 3.12 + FastAPI + httpx (streaming) |
| Backend principal | Bun + Elysia (TypeScript) |
| ORM | Drizzle ORM |
| Banco relacional | MySQL 8 |
| Migrações | Flyway |
| Front-end | HTML/CSS/JS puro (sem build step), servido via nginx |
| Infraestrutura | Docker + Docker Compose |
| Processamento de documentos | `pypdf` (PDF) + `openpyxl` (XLSX) |

> Tecnologia livre por decisão do enunciado ("total liberdade para escolher a linguagem/ecossistema"). O front não usa o template React de exemplo fornecido em aula porque o objetivo do trabalho é a base de conhecimento com IA generativa, e um front sem build step deixa o `docker compose up` mais simples e com menos pontos de falha.

## Pré-requisitos

Este projeto roda **inteiramente em containers**, incluindo o ChromaDB (banco vetorial), que só existe como imagem Docker oficial, sem instalação nativa alternativa. Por isso, **Docker Desktop é obrigatório**, não é uma opção entre várias.

- Windows 10 (build 19041+) ou Windows 11, 64-bit ou ARM64.
- Pelo menos 8GB de RAM livre (o modelo de IA + banco vetorial + MySQL rodam juntos).
- Conexão com internet na primeira subida (baixa as imagens Docker e o modelo de IA, ~2GB).

### Passo 1: Instalar o WSL2

O Docker Desktop no Windows depende do WSL2 (Windows Subsystem for Linux) por baixo.

1. Abra o **PowerShell como Administrador** (botão direito → "Executar como administrador").
2. Rode:
   ```powershell
   wsl --install
   ```
3. Reinicie o computador quando pedir.
4. Depois de reiniciar, o Windows deve terminar a instalação do WSL2 sozinho (pode abrir uma janela pedindo pra criar um usuário Linux; pode fechar, não é necessário pra esse projeto).
5. Pra confirmar que instalou certo, abra o PowerShell (não precisa ser Administrador dessa vez) e rode:
   ```powershell
   wsl --status
   ```
   Deve mostrar a versão padrão como **2**.

Se seu Windows já tiver o WSL2 instalado (`wsl --status` já funciona), pode pular esse passo.

### Passo 2: Instalar o Docker Desktop

1. Baixe em [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/) (escolha a versão certa: **x64** ou **ARM64**, dependendo do processador da máquina).
2. Instale normalmente (próximo, próximo, finalizar). Na tela de configuração, deixe a opção **"Use WSL 2 instead of Hyper-V"** marcada (é o padrão).
3. Abra o Docker Desktop e espere o ícone da baleia ficar estável (sem animação): indica que o motor do Docker subiu.
4. Confirme que funcionou abrindo um terminal (PowerShell) e rodando:
   ```powershell
   docker --version
   docker compose version
   ```
   Os dois precisam responder com um número de versão, sem erro.

## Guia de Execução (Passo a Passo)

Com Docker Desktop instalado e aberto:

1. **Clone o repositório** e entre na pasta do projeto:
   ```powershell
   git clone <url-do-repositorio>
   cd chat
   ```

2. **Copie o arquivo de variáveis de ambiente**:
   ```powershell
   copy .env.example .env
   ```
   O `.env.example` já vem com valores padrão que funcionam sem editar nada, só copiar é suficiente.

3. **Suba tudo com um único comando**:
   ```powershell
   docker compose up -d --build
   ```
   Isso sobe, na ordem certa e sozinho, sem nenhum passo manual:
   - MySQL (banco relacional)
   - Flyway (roda as migrações do banco automaticamente)
   - Ollama (baixa o modelo `qwen2.5:3b`, ~2GB, na primeira vez, pode levar alguns minutos)
   - ChromaDB (banco vetorial)
   - Backend Python (processa o PDF e o XLSX automaticamente ao iniciar, a "ingestão" roda sozinha, sem comando manual)
   - Backend Node (API principal)
   - Frontend (interface de chat)

   Alternativa, se tiver GPU **NVIDIA** dedicada disponível: use os scripts `start.ps1` (Windows) ou `start.sh` (Linux/Mac) na raiz do projeto, eles detectam a GPU sozinhos e sobem com aceleração quando possível, ou caem pro modo CPU normal se não tiver.

4. **Espere todos os serviços ficarem saudáveis** (a primeira subida demora mais, por causa do download do modelo de IA):
   ```powershell
   docker compose ps
   ```
   Todos os serviços devem aparecer como `Up` (mysql e ollama também mostram `healthy`).

5. **Acesse o chat** no navegador:
   ```
   http://localhost:5500
   ```

6. **Verifique a saúde da API** (opcional, pra debug):
   ```
   http://localhost:4000/health
   http://localhost:4000/health/python
   ```

### Portas usadas

| Serviço | Porta no host | O que é |
|---|---|---|
| Frontend (chat) | `5500` | Interface de chat no navegador |
| API Node | `4000` | Backend principal, orquestra tudo |
| API Python | `8001` | Serviço de IA/RAG |
| MySQL | `3310` | Banco relacional |
| ChromaDB | `8000` | Banco vetorial |
| Ollama | `11434` | Servidor do modelo de IA local |

### Para derrubar tudo

```powershell
docker compose down
```
(os dados do MySQL/Chroma/modelo do Ollama ficam guardados em volumes Docker, um `docker compose up -d` depois disso não perde nada nem baixa tudo de novo).

## Pontos Importantes

### 1. A primeira pergunta demora mais (download + carregamento do modelo)

Na primeiríssima subida, o `docker compose up -d --build` baixa o modelo `qwen2.5:3b` (~2GB) automaticamente antes de ficar pronto. Depois disso, o modelo fica carregado em memória (`keep_alive: 30m`), então perguntas seguintes não pagam esse custo de novo.

### 2. Sem GPU dedicada compatível, a IA responde via CPU (e isso é normal)

Este projeto roda 100% local, sem nenhuma API paga externa (restrição do enunciado). Sem uma GPU NVIDIA dedicada, o Ollama gera texto usando a CPU, o que é sensivelmente mais lento que um serviço de nuvem: **respostas que envolvem geração de texto real (não os atalhos de código) podem levar entre 20 segundos e alguns minutos**, dependendo do tamanho da pergunta e do hardware. Isso é esperado e não é bug: é o preço de rodar um LLM sem custo de API e sem GPU dedicada. O front-end mostra mensagens de status durante a espera pra deixar isso claro.

Se a máquina tiver GPU **NVIDIA** dedicada, use `docker compose -f docker-compose.yml -f docker-compose.gpu.yml up -d --build` (ou os scripts `start.ps1`/`start.sh`, que detectam isso sozinhos) para acelerar a geração de verdade.

### 3. Ativar "Alto desempenho" no Windows ajuda bastante em CPU sem GPU

Notebooks configurados com o plano de energia **"Equilibrado"** (o padrão do Windows) limitam a frequência do processador de propósito, mesmo com o notebook na tomada. Isso reduz a velocidade real de geração da IA. Ativar o plano **"Alto desempenho"** remove esse limite artificial.

**Automático (recomendado):** abra uma janela do PowerShell e rode:
```powershell
powershell -ExecutionPolicy Bypass -File power-boost-listener.ps1
```
Deixe essa janela aberta durante os testes. Ela ativa "Alto desempenho" automaticamente assim que uma pergunta começa a ser processada pela IA, e volta pro "Equilibrado" assim que a resposta termina, sem precisar fazer nada manualmente. É totalmente opcional: se essa janela não estiver aberta, o chat funciona normalmente do mesmo jeito, só sem esse ganho extra de velocidade.

**Manual, se preferir:**
```powershell
powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c
```
E pra voltar ao normal depois:
```powershell
powercfg /setactive 381b4222-f694-41f0-9685-ff5bb260df2e
```

### 4. Uma pergunta por vez

O sistema processa uma pergunta de IA por vez, de propósito: se uma segunda pergunta chegar enquanto a primeira ainda está sendo gerada, ela recebe uma mensagem pedindo pra esperar, em vez de entrar numa fila escondida (decisão consciente: enfileirar sem avisar já causou confusão em testes, porque a pessoa não sabia que a pergunta dela estava "presa" atrás de outra).

### 5. Limitações conhecidas do modelo local

Por ser um modelo pequeno (3B parâmetros, escolhido pra caber no hardware sem GPU), o Qwen ocasionalmente erra contagens exatas (ex: "quantos profissionais" pode contar 1 a mais/menos que o real) mesmo quando o dado correto foi recuperado certinho do banco vetorial: é limite de raciocínio do modelo, não erro de busca de dados.

## Estrutura do Projeto

```
chat/
├── api/                  # Backend Node (Elysia + Drizzle + MySQL)
│   ├── db/migration/     # Migrações Flyway (V1, V2, V3)
│   ├── src/db/           # Schema Drizzle + queries
│   ├── src/modules/      # config.ts (env), ia-stream.ts (streaming/log)
│   └── index.ts          # Rotas da API
├── ia/                   # Backend Python (RAG + Ollama)
│   ├── dados/            # PDF, XLSX e SQL de exemplo usados na ingestão
│   ├── modules/          # config.py, modelos.py, rag.py, regras.py, criterio.py, geracao.py
│   └── main.py           # Rotas FastAPI
├── frontend/              # Chat (HTML/CSS/JS puro) + Dockerfile (nginx)
├── documentacao/          # Documentação de escopo, backlog e decisões técnicas
├── docker-compose.yml     # Orquestração principal (CPU)
├── docker-compose.gpu.yml # Override opcional pra GPU NVIDIA
├── power-boost-listener.ps1  # Opcional: ativa "Alto desempenho" durante a geração
└── start.ps1 / start.sh   # Sobe o projeto detectando GPU automaticamente
```
