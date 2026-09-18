# Brief — Gerar planilha XLSX "Preços e Profissionais"

## Contexto (projeto)
Trabalho de faculdade (Sistemas Inteligentes) que precisa entregar um chat de IA generativa (RAG) 100% local. Uma das fontes obrigatórias de dados é uma **planilha .XLSX** com preços/pacotes de sessão e a lista de profissionais/horários. Essa planilha entra na mesma base de conhecimento (embeddings) que o PDF institucional do mesmo projeto — os dois documentos precisam ser consistentes entre si (mesmo elenco de profissionais e especialidades).

A clínica de referência é o **Instituto Luz** (fisioterapia), São Luís/MA. O elenco de profissionais é **real** (extraído do sistema de gestão da própria clínica). Só os **preços/pacotes são dado fictício** (o sistema real não expõe preço, isso é exclusivo desse trabalho acadêmico) — devem ser plausíveis pra uma clínica de fisioterapia de porte médio no Brasil.

## Elenco de profissionais (REAL — extraído do banco de dados do sistema SmartClinic em 16/09/2026, não é fictício; usar EXATAMENTE estes nomes/especialidades — precisa bater com o Guia do Paciente e o banco MySQL do mesmo projeto)
- **Fernanda de Sousa Negreiros** — Traumato ortopedia e esportiva
- **Amorim Da Silva De Menezes** — Fisioterapia respiratória
- **Antonio Mateus da Silva Aguiar** — Osteopatia
- **Beatriz Da Luz Sousa Lima** — Osteopatia
- **Guimarães Sousa Costa Rayanne** — Osteopatia
- **Ana Lívia Silva De Sousa** — Pilates
- **Luan Eduardo Oliveira da Silva** — Pilates

As especialidades "fisioterapia em traumatologia e esporte", "assimetria craniana" e "injetáveis" existem no cadastro real do sistema mas sem profissional ativo no momento — pode aparecer na aba de preços (a clínica cobra por elas), mas não invente profissional pra elas na aba de horários.

## Estrutura pedida (2 abas)

### Aba 1 — "Precos_Pacotes"
Colunas: `especialidade`, `tipo_sessao` (ex: avaliação inicial, sessão avulsa, pacote 4 sessões, pacote 8 sessões, pacote 12 sessões), `preco_unitario` (R$), `preco_total` (R$), `validade_dias` (prazo pra usar o pacote), `observacao` (texto curto, ex: "sessões semanais", "inclui avaliação").

Gerar uma linha de avaliação inicial + pelo menos 3 opções de pacote por especialidade (avulsa, 4, 8 sessões), preços plausíveis pro mercado brasileiro de fisioterapia/pilates (ex: sessão avulsa R$ 90–150, pacotes com desconto progressivo).

### Aba 2 — "Profissionais_Horarios"
Colunas: `nome`, `especialidade`, `dias_atendimento` (ex: "Segunda, Quarta, Sexta"), `horario_inicio`, `horario_fim`, `anos_experiencia`.

Uma linha por profissional (os 7 listados acima), horários dentro da janela real de funcionamento da clínica (segunda a sexta, 8h às 18h), sem sobreposição total entre todos (varie os dias/horários de cada um pra parecer uma agenda real). `anos_experiencia` é fictício aqui (não veio do sistema real).

## O que gerar
As duas tabelas completas, em formato que dê pra virar `.xlsx` diretamente — se você tiver ferramenta pra gerar arquivo Excel de verdade, gere o `.xlsx` com as duas abas nomeadas exatamente como acima. Se não tiver, gere duas tabelas em markdown (uma por aba, com o nome da aba como título) prontas pra colar no Excel/Google Sheets e depois exportar como `.xlsx`.

## Restrição
Nenhum dado de paciente real ou fictício aqui — só preços, pacotes e agenda de profissionais.
