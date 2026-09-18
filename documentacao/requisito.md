# Requisito oficial — Trabalho prático (Sistemas Inteligentes)

Enunciado publicado no AVA por Edilson Carlos Silva Lima, sexta-feira 28/08/2026.

## Desenvolvimento de Base de Conhecimento com IA Generativa (vale até 50% da nota)

### Pontuação
- Peso: 50% da nota do 1º Bimestre.
- Bônus de Excelência: se a solução estiver 100% funcional e com alto padrão de qualidade, também compõe 50% da nota do 2º Bimestre.

### O desafio
Com base no notebook KLM (NotebookLM) apresentado em sala — front em anexo (`tde-ia.zip`) —, desenvolver uma Base de Conhecimento utilizando IA Generativa: uma solução de Chat de IA onde o usuário interage e extrai informações dos documentos fornecidos.

- **Modelo base:** o projeto anexo só tem a estrutura de front-end (React). **Decisão do grupo: esse front é banal, vamos usar como referência de intenção mas construir o nosso próprio front.**
- **Tecnologias:** liberdade total de linguagem/ecossistema.
- **Restrição crucial:** proibido usar API externa paga/pública (OpenAI, Anthropic, etc.) na versão final — precisa ser API local própria, usando frameworks (ex: Ollama).

### Requisitos de dados e armazenamento
A solução deve obrigatoriamente processar e recuperar informação dos seguintes formatos (arquivos anexados ao post):
1. Documento em PDF
2. Planilha em .XLSX (Excel)
3. Banco de dados MySQL
4. Opcional: integração com MongoDB

### Formato de trabalho e entrega
- Individual ou em dupla.
- **Prazo final:** 11/09/2026 no AVA + apresentar funcionando ao professor (**adiado pelo professor para sexta-feira 18/09/2026**, confirmado em 16/09/2026).
- Sem apresentação formal em slides — validação ao vivo no laboratório, aluno/dupla explica o funcionamento do código e da solução direto pro professor.

### O que precisa estar no repositório (GitHub/GitLab)
`README.md` impecável contendo:
- Descrição do projeto (escopo e o que a solução faz)
- Tecnologias utilizadas (todas as ferramentas, linguagens e bibliotecas)
- Guia de execução passo a passo: instalar dependências, rodar a API local, subir o banco de dados, executar o front-end

Arquivos de exemplo (front React + bases de dados) já vieram anexados ao post original (`tde-ia.zip`).

---

Ver [`escopo.md`](./escopo.md) para o escopo funcional e a arquitetura que decidimos para atender esse requisito.
