# Testes de tempo de resposta — Instituto Luz Chat

Bateria de perguntas cobrindo todo o escopo funcional (especialidades, preços,
políticas, disponibilidade, cumprimento), cronometradas via `POST /chat`
(caminho real: front → Node → Python/Ollama ou Node → MySQL direto).

Máquina: CPU local, sem GPU (Ollama `llama3.2:3b`).

| # | Pergunta | Canal | Tempo | Resposta |
|---|----------|-------|-------|----------|
| 1 | oi | - | 0.1s | Boa tarde! Sou o assistente virtual do Instituto Luz. Como posso te ajudar hoje?  |
| 2 | Quais especialidades voces atendem? | - | 72.9s | O Instituto Luz oferece dois serviços importantes: Fisioterapia e Osteopatia. Ambas são especialidades de saúde que podem ajudar a melhorar a qualidade de vida de nossos pacientes.  |
| 3 | Quanto custa um pacote de 4 sessoes de osteopatia? | - | 91.1s |   Desculpe, o assistente demorou demais pra responder. Tente novamente ou reformule a pergunta de um jeito mais direto.  |
| 4 | Qual a politica de falta? | - | 93.0s |   Desculpe, o assistente demorou demais pra responder. Tente novamente ou reformule a pergunta de um jeito mais direto.  |
| 5 | Tem horario disponivel de pilates? | - | 0.4s | Aqui está a disponibilidade encontrada: Fernanda de Sousa Negreiros (Traumato ortopedia e esportiva): segunda das 08:00:00 às 12:00:00; Fernanda de Sousa Negreiros (Traumato ortopedia e esportiva): quarta das 08:00:00 às 12:00:00; Fernanda de Sousa Negreiros (Traumato ortopedia e esportiva): sexta das 08:00:00 às 12:00:00; Amorim Da Silva De Menezes (Fisioterapia respiratoria): terca das 13:00:00 às 18:00:00; Amorim Da Silva De Menezes (Fisioterapia respiratoria): quinta das 13:00:00 às 18:00:00; Antonio Mateus da Silva Aguiar (Osteopatia): segunda das 08:00:00 às 13:00:00; Antonio Mateus da Silva Aguiar (Osteopatia): terca das 08:00:00 às 13:00:00; Antonio Mateus da Silva Aguiar (Osteopatia): quinta das 08:00:00 às 13:00:00.  |
| 6 | Voces atendem criancas? | - | 66.8s | Sim, o Instituto Luz atende crianças, especialmente na especialidade de assimetria craniana, voltada a bebês nos primeiros meses de vida.  |
| 7 | Onde fica a clinica e qual o horario de funcionamento? | - | ~~0.2s~~ 74.7s | ~~Aqui está a disponibilidade encontrada: [dump errado, bug de roteamento]~~ O Instituto Luz está localizado em São Luís, Maranhão, e tem horário de funcionamento de segunda a sexta-feira, das 8h às 18h. Além disso, é possível agendar consultas e sessões por WhatsApp, com o número (99) 98263-8573. |

**Bug de roteamento corrigido durante essa bateria**: a palavra "horário" sozinha disparava a rota de disponibilidade (MySQL) mesmo em perguntas institucionais como "horário de funcionamento" — devolvia a grade de profissionais em vez da resposta certa. Corrigido em `chat/api/index.ts`: agora só conta como disponibilidade quando "horário" aparece junto de "livre"/"disponível"/"tem horário" (ou as palavras "disponibilidade", "agenda", "vaga"/"vago" sozinhas). Reexecutei a pergunta #7 depois da correção — linha acima já reflete o resultado certo.

**Timeouts observados (perguntas #3 e #4, 91-93s)**: bateram no teto de 90s do Python em duas das sete perguntas dessa bateria, mesmo com `num_predict=200`. Não é bug novo — é variação de carga da CPU rodando vários testes em sequência (mesma pergunta isolada, testada antes e depois, respondeu em 40-90s de forma inconsistente). Registrado como limitação conhecida, não resolvido nessa sessão.

**Especialidades incompletas (pergunta #2)**: respondeu só "Fisioterapia e Osteopatia" (real são 7: Pilates, Osteopatia, Fisioterapia respiratória, Traumato-ortopedia e esportiva, Fisioterapia em traumatologia e esporte, Assimetria craniana, Injetáveis). Limitação conhecida do chunking genérico — a lista completa de especialidades está espalhada em vários chunks do PDF, e a busca (top_k=4) nem sempre traz todos. Não resolvido nessa sessão (aumentar top_k ainda mais pioraria a velocidade, já apertada).

Gerado em 2026-09-17 14:26:44, atualizado 2026-09-17 (pós-correção de roteamento)
