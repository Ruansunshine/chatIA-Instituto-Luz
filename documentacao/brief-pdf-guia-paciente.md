# Brief — Gerar conteúdo do PDF "Guia do Paciente"

## Contexto (projeto)
Trabalho de faculdade (Sistemas Inteligentes) que precisa entregar um chat de IA generativa (RAG) 100% local, capaz de responder dúvidas de pacientes consultando uma base de conhecimento própria. Uma das fontes obrigatórias é um **PDF institucional "Guia do Paciente"**, que vai ser convertido em embeddings (ChromaDB) e servir de base pra o chat responder perguntas sobre especialidades e políticas da clínica.

A clínica de referência é o **Instituto Luz** (fisioterapia), em São Luís/MA. Abaixo estão fatos reais extraídos do site institucional (`instituto-luz-revive.lovable.app`) — use-os como base real. O restante (políticas detalhadas, elenco completo de profissionais) é fictício, criado pra fins acadêmicos, e deve ficar claro que é fictício se alguém perguntar (mas não precisa de aviso dentro do próprio texto do guia — o guia deve soar como documento institucional real).

## Fatos reais (usar como base)
- **Missão**: promover saúde e qualidade de vida por meio de atendimento humano, ético e baseado em evidências.
- **Visão**: ser referência em cuidado, prevenção e reabilitação, trazendo clareza e confiança.
- **Diferenciais**: avaliação completa, tratamento personalizado, resultados rápidos, profissionais especializados, atendimento humanizado.
- **Funcionamento**: segunda a sexta, 8h às 18h.
- **Localização**: São Luís, Maranhão.
- **Contato**: WhatsApp (99) 98263-8573, e-mail luzbeatriz139@gmail.com.
- **Especialidades oferecidas** — o site de marketing usa nomes simplificados, mas o sistema real de gestão da clínica (SmartClinic) usa outra taxonomia, mais autoritativa por ser o cadastro efetivo. Use os nomes reais do sistema (expandir cada um em um parágrafo completo no guia, com descrição acessível pro paciente leigo):
  1. Pilates — fortalecimento, flexibilidade e equilíbrio corporal.
  2. Osteopatia — avaliação e tratamento manual, cuidado especializado.
  3. Fisioterapia respiratória — tratamento de questões respiratórias.
  4. Traumato-ortopedia e esportiva — reabilitação de lesões ortopédicas e esportivas.
  5. Fisioterapia em traumatologia e esporte — existe no cadastro, sem profissional ativo no momento; mencionar como serviço oferecido, sem citar profissional.
  6. Assimetria craniana — existe no cadastro, sem profissional ativo no momento; mencionar como serviço oferecido, sem citar profissional.
  7. Injetáveis — existe no cadastro, sem profissional ativo no momento; mencionar como serviço oferecido, sem citar profissional.

## Elenco de profissionais (REAL — extraído do banco de dados do sistema SmartClinic em 16/09/2026, não é fictício; usar EXATAMENTE estes nomes/especialidades — precisa bater com a planilha de preços e o banco MySQL do mesmo projeto)
- **Fernanda de Sousa Negreiros** — Traumato ortopedia e esportiva (CREFITO 338657-F)
- **Amorim Da Silva De Menezes** — Fisioterapia respiratória (CREFITO 268906-F)
- **Antonio Mateus da Silva Aguiar** — Osteopatia (CREFITO 343917-F)
- **Beatriz Da Luz Sousa Lima** — Osteopatia (CREFITO 265099-F)
- **Guimarães Sousa Costa Rayanne** — Osteopatia (CREFITO 286674-F)
- **Ana Lívia Silva De Sousa** — Pilates (CREFITO 387999-F)
- **Luan Eduardo Oliveira da Silva** — Pilates (CREFITO 000000)

Nas especialidades sem profissional ativo (fisioterapia em traumatologia e esporte, assimetria craniana, injetáveis), não invente nome — descreva o serviço sem atribuir a um profissional específico.

## O que gerar
Texto completo e corrido do "Guia do Paciente" (markdown ou texto simples, pronto pra ser exportado/impresso como PDF depois), em português, tom institucional (não técnico, não robótico), contendo:

1. **Apresentação** — quem é o Instituto Luz, missão, visão, localização, horário de funcionamento, contato.
2. **Especialidades** — uma seção por especialidade (as 5 listadas acima), cada uma com um parágrafo (~80-150 palavras) explicando o que é, quando é indicada, o que esperar do atendimento, e o nome do profissional responsável.
3. **Política de agendamento** — invente de forma plausível: como marcar (WhatsApp ou presencial), antecedência mínima, o que acontece se o horário não estiver disponível.
4. **Política de cancelamento** — invente de forma plausível: prazo mínimo pra cancelar sem custo/penalidade, o que acontece com cancelamento em cima da hora.
5. **Política de falta** — invente de forma plausível: o que acontece se o paciente não comparecer e não avisar (ex: perda da sessão do pacote, necessidade de reagendar, limite de faltas antes de alguma consequência).
6. **Perguntas frequentes** (opcional, 3-5 perguntas curtas) — cobrindo dúvidas que um paciente real faria (ex: "preciso de encaminhamento médico?", "posso remarcar quantas vezes?").

## Tamanho alvo
800–1500 palavras, com headings claros (##) por seção — importante para o chunking do RAG recuperar o trecho certo por especialidade/política.

## Saída esperada
Um único bloco de texto/markdown pronto pra colar num editor e exportar como PDF (ex: Google Docs → Download PDF, ou pandoc). Não precisa gerar o PDF binário em si, só o conteúdo textual formatado.
