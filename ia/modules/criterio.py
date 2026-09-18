"""Criterio de decisao: quando uma regra do assistente vira PROMPT (texto que
o Ollama interpreta) e quando vira CODIGO (funcao Python deterministica).
Arquivo unico de referencia - nao mistura com a implementacao em si
(SYSTEM_PROMPT e as funcoes de codigo continuam em modules/regras.py).

Por que isso importa: o Ollama nao "aprende" nem "guarda" o prompt entre
chamadas - toda pergunta reprocessa o SYSTEM_PROMPT inteiro do zero (nada de
cache de entendimento; o `keep_alive` so mantem o PESO do modelo na memoria,
nao o raciocinio de uma conversa anterior). Ou seja:
  - prompt maior = mais token = mais lento, sempre, em toda chamada.
  - prompt nao e' garantia de comportamento - e' geracao probabilistica, nao
    execucao de codigo. Um modelo pequeno (3b) pode "ler" uma regra
    condicional e ainda assim nao segui-la.

Regra de decisao (aplicar antes de adicionar qualquer regra nova):
  - Se da pra resolver com codigo simples (regex, comparacao de data/hora,
    lookup em banco) E a resposta e sempre a mesma pro mesmo caso -> CODIGO.
    Mais rapido (pode ate pular a chamada ao Ollama inteira), 100%
    confiavel, nao cresce o prompt.
  - Se exige entender linguagem livre do usuario, gerar texto novo, ou
    julgar caso a caso (tom, resistir a pegadinha, responder pergunta
    aberta) -> PROMPT. Nao da pra escrever isso como regex.

Catalogo abaixo - atualizar sempre que uma regra nova for adicionada ou uma
regra de prompt for migrada pra codigo (como aconteceu com o cumprimento por
horario, ver ultima linha).
"""

CATALOGO = [
    {
        "regra": "Identidade e tom (quem e' o assistente, como fala)",
        "tipo": "prompt",
        "onde": "SYSTEM_PROMPT em modules/regras.py",
        "motivo": "exige geracao de linguagem natural consistente",
    },
    {
        "regra": "Nao usar linguagem ofensiva / xingamento",
        "tipo": "prompt + codigo (defesa em camadas)",
        "onde": (
            "SYSTEM_PROMPT regra 2 (modelo nao xinga de volta) + "
            "PALAVRAS_BLOQUEADAS/contem_conteudo_bloqueado (bloqueia ANTES "
            "de chamar o modelo) em modules/regras.py"
        ),
        "motivo": "nao depende so do modelo obedecer - filtro de codigo garante mesmo se o prompt falhar",
    },
    {
        "regra": "Nao dar diagnostico/prescricao medica",
        "tipo": "prompt",
        "onde": "SYSTEM_PROMPT regra 3",
        "motivo": "exige julgar se a pergunta e' clinica, caso a caso, em linguagem livre",
    },
    {
        "regra": "Nao inventar informacao sem certeza",
        "tipo": "prompt",
        "onde": "SYSTEM_PROMPT regra 4",
        "motivo": "exige o modelo avaliar a propria confianca na resposta",
    },
    {
        "regra": "Nao discutir assunto fora do escopo da clinica",
        "tipo": "prompt",
        "onde": "SYSTEM_PROMPT regra 5",
        "motivo": "exige entender o tema da pergunta - aberto demais pra regex",
    },
    {
        "regra": "Resistir a pedido pra ignorar as regras (prompt injection)",
        "tipo": "prompt",
        "onde": "SYSTEM_PROMPT regra 6",
        "motivo": "exige interpretar a intencao do usuario em linguagem livre",
    },
    {
        "regra": "Respostas curtas, sem markdown",
        "tipo": "prompt",
        "onde": "SYSTEM_PROMPT regra 7",
        "motivo": "e' sobre estilo da geracao - so da pra pedir, nao forcar por fora sem cortar o texto",
    },
    {
        "regra": "Data/hora atual da conversa (nao cair em pegadinha de data)",
        "tipo": "prompt, com dado injetado por codigo",
        "onde": "montar_system_prompt() em modules/regras.py",
        "motivo": (
            "o VALOR da data e' calculado em codigo (datetime real, sem "
            "chance de erro), mas precisa entrar no texto do prompt pra o "
            "modelo usar em perguntas abertas tipo 'quando voces abrem "
            "depois de amanha'"
        ),
    },
    {
        "regra": "Cumprimento (bom dia/boa tarde/boa noite) bater com o horario real",
        "tipo": "codigo",
        "onde": (
            "eh_apenas_saudacao / saudacao_do_horario_atual / "
            "resposta_saudacao em modules/regras.py, "
            "curto-circuito em main.py antes de chamar o Ollama"
        ),
        "motivo": (
            "TESTADO na pratica: como regra de prompt, o modelo 3b nao "
            "seguia de forma confiavel (respondeu 'Boa manha' ecoando o "
            "usuario mesmo sendo madrugada). Resposta e' sempre a mesma pro "
            "mesmo horario -> vira codigo, nem chama o Ollama (0.1s vs ~14s)"
        ),
    },
    {
        "regra": "Disponibilidade de horario (grade real de profissionais)",
        "tipo": "codigo (fora do servico Python, no backend Node)",
        "onde": "buscarDisponibilidade em chat/api/src/db/queries.ts, roteado em POST /chat",
        "motivo": "e' consulta direta no MySQL, dado estruturado - nao ha nada pro modelo interpretar, so' buscar e formatar",
    },
]
