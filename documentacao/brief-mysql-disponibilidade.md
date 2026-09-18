# Brief — Gerar schema + seed do MySQL "Grade de Disponibilidade"

## Contexto (projeto)
Trabalho de faculdade (Sistemas Inteligentes) que precisa entregar um chat de IA generativa (RAG) 100% local. Uma das fontes obrigatórias de dados é um **banco MySQL estruturado** com a grade de disponibilidade de horário por especialidade/profissional — essa é a única fonte que NÃO passa por embedding/RAG: o backend consulta direto no MySQL (endpoint `GET /disponibilidade`) e monta a resposta, sem passar pelo Ollama pra esse tipo de pergunta.

Stack do backend: **Drizzle ORM + MySQL, schema versionado via Flyway** (migrações em `db/migration/V1__descricao.sql`, sem módulos, API enxuta). O schema e o seed devem vir como um único arquivo SQL de migração Flyway.

A clínica de referência é o **Instituto Luz** (fisioterapia), São Luís/MA, funcionamento segunda a sexta, 8h às 18h. Especialidades e profissionais são **reais** (extraídos do banco do SmartClinic); só a **grade de horários (dia/hora) é fictícia** — o sistema real não modela disponibilidade em grade fixa, então essa parte é inventada pra fins do trabalho, sem integração real.

## Elenco de profissionais/especialidades (REAL — extraído do banco de dados do sistema SmartClinic em 16/09/2026, não é fictício; usar EXATAMENTE estes nomes/especialidades — precisa bater com o Guia do Paciente e a planilha de preços do mesmo projeto)
- **Fernanda de Sousa Negreiros** — Traumato ortopedia e esportiva
- **Amorim Da Silva De Menezes** — Fisioterapia respiratória
- **Antonio Mateus da Silva Aguiar** — Osteopatia
- **Beatriz Da Luz Sousa Lima** — Osteopatia
- **Guimarães Sousa Costa Rayanne** — Osteopatia
- **Ana Lívia Silva De Sousa** — Pilates
- **Luan Eduardo Oliveira da Silva** — Pilates

Especialidades "fisioterapia em traumatologia e esporte", "assimetria craniana" e "injetáveis" também existem no cadastro real, mas sem profissional ativo — inclua na tabela `especialidades`, mas não crie profissional fictício pra elas.

## Schema pedido
Tabelas simples, sem over-engineering (é um trabalho de faculdade, API "enxuta, sem módulos"):

1. **`especialidades`** — `id` (PK), `nome`, `descricao_curta`.
2. **`profissionais`** — `id` (PK), `nome`, `especialidade_id` (FK), `anos_experiencia`.
3. **`disponibilidade`** — `id` (PK), `profissional_id` (FK), `dia_semana` (enum ou string: segunda..sexta), `horario_inicio` (TIME), `horario_fim` (TIME), `duracao_slot_minutos` (ex: 50), `vagas_por_slot` (int, default 1).

Sem tabela de agendamento real nem de paciente — é só a grade de disponibilidade (quando cada profissional atende), não quem já ocupou o horário.

## O que gerar
Um arquivo `.sql` único, no formato de migração Flyway (`V1__cria_grade_disponibilidade.sql`), contendo:
1. `CREATE TABLE` das 3 tabelas acima, com FKs e tipos MySQL corretos (InnoDB, utf8mb4).
2. `INSERT` de seed:
   - As 7 especialidades reais listadas acima (as 4 com profissional ativo + as 3 sem: fisioterapia em traumatologia e esporte, assimetria craniana, injetáveis).
   - Os 7 profissionais reais listados acima, cada um ligado à sua especialidade.
   - Disponibilidade de cada um dos 7 profissionais: pelo menos 3 dias da semana por profissional, dentro da janela 08:00–18:00, com blocos de horário plausíveis (ex: "Beatriz Da Luz Sousa Lima — segunda, quarta, sexta, 08:00–12:00", dado fictício). Varie os dias/horários entre profissionais pra não sobrepor todos ao mesmo tempo (parecer uma agenda real de clínica).

## Saída esperada
Bloco de código SQL único, comentado em português nas seções (`-- especialidades`, `-- profissionais`, `-- disponibilidade`), pronto pra salvar como arquivo de migração Flyway.
