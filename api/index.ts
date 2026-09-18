import { Elysia, t } from "elysia";
import { cors } from "@elysiajs/cors";
import { swagger } from "@elysiajs/swagger";
import { sql } from "drizzle-orm";
import { db } from "./src/db/client";
import { buscarDisponibilidade, buscarHistoricoConversa, registrarConversa } from "./src/db/queries";
import { CORS_ORIGINS, HOST, IS_DEV, PORT, PYTHON_SERVICE_URL } from "./src/modules/config";
import { iaEstaOcupada, liberarIa, marcarIaOcupada, streamComLog } from "./src/modules/ia-stream";

const app = new Elysia()
  .onAfterHandle(({ set }) => {
    set.headers["X-Content-Type-Options"] = "nosniff";
    set.headers["X-Frame-Options"] = "DENY";
    set.headers["Referrer-Policy"] = "no-referrer";
  })
  .get(
    "/",
    () => ({
      success: true,
      message: "Instituto Luz - Chat API online",
      ...(IS_DEV ? { docs: "/docs" } : {}),
    }),
    { detail: { tags: ["System"], summary: "API root" } }
  )
  .get(
    "/health",
    async () => {
      try {
        await db.execute(sql`SELECT 1`);
        return { success: true, status: "ok", db: "connected" };
      } catch (error) {
        return {
          success: false,
          status: "error",
          db: "error",
          error: error instanceof Error ? error.message : String(error),
        };
      }
    },
    { detail: { tags: ["System"], summary: "Health check (API + MySQL)" } }
  )
  .get(
    "/disponibilidade",
    async ({ query }) => {
      const linhas = await buscarDisponibilidade({
        especialidade: query.especialidade,
        profissional: query.profissional,
      });
      return { success: true, total: linhas.length, disponibilidade: linhas };
    },
    {
      detail: {
        tags: ["Disponibilidade"],
        summary: "Consulta a grade de disponibilidade (direto no MySQL, sem passar pela IA)",
      },
    }
  )
  .get(
    "/chat/historico",
    async ({ query }) => {
      const sessionId = query.sessionId;
      if (!sessionId) return { success: false, historico: [] };
      const historico = await buscarHistoricoConversa(sessionId);
      return { success: true, historico };
    },
    {
      query: t.Object({ sessionId: t.String() }),
      detail: {
        tags: ["Chat"],
        summary: "Retorna o historico da sessao (mesma janela usada como memoria pro Ollama) - usado pra reconstruir a tela apos um refresh",
      },
    }
  )
  .post(
    "/chat",
    async ({ body, set }) => {
      const pergunta = body.pergunta.trim();
      const sessionId = body.sessionId;
      const perguntaLower = pergunta.toLowerCase();
      // "horario"/"horário" sozinho e' ambiguo demais - pega tambem
      // "horário de funcionamento" (que nao e' disponibilidade de agenda,
      // e' informacao institucional, deve ir pro RAG). So conta como
      // disponibilidade quando "horario" aparece junto de palavra que
      // sinaliza vaga/agenda de profissional.
      const PALAVRAS_DISPONIBILIDADE = [
        "disponibilidade",
        "agenda",
        "vaga",
        "vago",
        "horario livre",
        "horário livre",
        "horario disponivel",
        "horário disponível",
        "tem horario",
        "tem horário",
      ];
      const ehSobreDisponibilidade = PALAVRAS_DISPONIBILIDADE.some((palavra) =>
        perguntaLower.includes(palavra)
      );

      if (ehSobreDisponibilidade) {
        const linhas = await buscarDisponibilidade({});
        const resposta =
          linhas.length === 0
            ? "Não encontrei horários cadastrados no momento."
            : `Aqui está a disponibilidade encontrada: ${linhas
                .slice(0, 8)
                .map(
                  (linha) =>
                    `${linha.profissional} (${linha.especialidade}): ${linha.diaSemana} das ${linha.horarioInicio} às ${linha.horarioFim}`
                )
                .join("; ")}.`;

        await registrarConversa(sessionId, pergunta, resposta, "mysql");
        set.headers["X-Fontes"] = "MySQL - grade de disponibilidade";
        set.headers["Content-Type"] = "text/plain; charset=utf-8";
        return resposta;
      }

      if (iaEstaOcupada()) {
        set.status = 429;
        set.headers["Content-Type"] = "text/plain; charset=utf-8";
        return "O assistente já está processando outra pergunta agora. Espera uns segundos e tenta de novo.";
      }

      // So limita o tempo pra CONECTAR e receber os headers do Python - uma
      // vez que o stream comecou a chegar, deixa rolar (o Python ja tem seu
      // proprio timeout/corte interno pro Ollama, ver chat/ia/main.py).
      const controle = new AbortController();
      const limiteConexao = setTimeout(() => controle.abort(), 15_000);

      marcarIaOcupada();
      try {
        const historico = await buscarHistoricoConversa(sessionId);
        const res = await fetch(`${PYTHON_SERVICE_URL}/responder`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ pergunta, historico }),
          signal: controle.signal,
        });
        clearTimeout(limiteConexao);

        if (!res.ok || !res.body) {
          throw new Error(`Servico Python respondeu ${res.status}`);
        }

        const fontesPython = res.headers.get("X-Fontes");
        if (fontesPython) {
          set.headers["X-Fontes"] = fontesPython;
        }
        set.headers["Content-Type"] = "text/plain; charset=utf-8";
        // iaEstaOcupada volta pra false quando o stream fechar de verdade
        // (ver src/ia-stream.ts) - continua "true" durante todo o streaming,
        // que e' quando o Ollama esta genuinamente ocupado.
        return streamComLog(res.body, sessionId, pergunta, "ia");
      } catch (error) {
        liberarIa();
        clearTimeout(limiteConexao);
        set.status = 502;
        set.headers["Content-Type"] = "text/plain; charset=utf-8";
        const foiTimeout = error instanceof Error && error.name === "AbortError";
        return foiTimeout
          ? "Desculpe, o assistente não respondeu a tempo. Tente novamente em instantes."
          : "Desculpe, não consegui falar com o assistente agora. Tente novamente em instantes.";
      }
    },
    {
      body: t.Object({ pergunta: t.String(), sessionId: t.String() }),
      detail: {
        tags: ["Chat"],
        summary:
          "Orquestra a resposta (streaming): disponibilidade resolve direto no MySQL, o resto repassa pro servico Python (Ollama)",
      },
    }
  )
  .get(
    "/health/python",
    async () => {
      try {
        const res = await fetch(`${PYTHON_SERVICE_URL}/health`);
        const body = await res.json();
        return { success: true, reachable: true, python: body };
      } catch (error) {
        return {
          success: false,
          reachable: false,
          error: error instanceof Error ? error.message : String(error),
        };
      }
    },
    {
      detail: {
        tags: ["System"],
        summary: "Verifica comunicacao Node -> Python (proxy de health check)",
      },
    }
  )
  .use(
    cors({
      origin: CORS_ORIGINS,
      methods: ["GET", "POST", "OPTIONS"],
      allowedHeaders: ["Content-Type"],
      exposeHeaders: ["X-Fontes"],
      credentials: false,
    })
  );

if (IS_DEV) {
  app.use(
    swagger({
      path: "/docs",
      documentation: {
        info: {
          title: "Instituto Luz - Chat API",
          version: "0.1.0",
          description:
            "API do trabalho de Sistemas Inteligentes (base de conhecimento com IA generativa).",
        },
      },
    })
  );
}

// idleTimeout padrao do Bun.serve e' baixo (segundos) - matava a conexao no
// meio de uma resposta em streaming da IA (que legitimamente demora mais que
// isso pra comecar a responder). Achado via log: Elysia chamava pull() e
// recebia bytes do Python, mas o cliente via conexao vazia/fechada antes
// disso - o servidor estava derrubando a conexao por timeout de ociosidade.
//
// 250 - o Bun.serve recusa qualquer valor acima de 255 (TypeError na subida,
// derrubando a API inteira - aconteceu na pratica testando aqui, corrigido
// antes de virar problema em producao). Fica sempre MAIOR que o teto do
// Python (TIMEOUT_OLLAMA em chat/ia/modules/geracao.py, hoje 200s) - com os
// dois empatados antes (120s/120s), era corrida: se o Bun cortasse primeiro,
// o cliente recebia conexao vazia em vez da mensagem de erro do Python
// (confirmado testando as duas pontas isoladas). Node maior garante que a
// mensagem do Python sempre chega antes do Bun desistir.
app.listen({ port: PORT, hostname: HOST, idleTimeout: 250 });

console.log(
  `Elysia rodando em http://${HOST}:${app.server?.port}${IS_DEV ? " | Docs: /docs" : ""}`
);
