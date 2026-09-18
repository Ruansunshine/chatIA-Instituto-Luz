import { and, desc, eq, like } from "drizzle-orm";
import { db } from "./client";
import { conversas, disponibilidade, especialidades, profissionais } from "./schema";

// Quantas trocas (pergunta+resposta) da MESMA sessao mandar como historico
// pro Ollama. Limitado de proposito - cada troca a mais e' mais token
// reprocessado do zero em toda chamada (ver criterio em chat/ia/modules).
const LIMITE_HISTORICO = 4;

export async function buscarDisponibilidade(filtros: {
  especialidade?: string;
  profissional?: string;
}) {
  const condicoes = [];
  if (filtros.especialidade) {
    condicoes.push(like(especialidades.nome, `%${filtros.especialidade}%`));
  }
  if (filtros.profissional) {
    condicoes.push(like(profissionais.nome, `%${filtros.profissional}%`));
  }

  return db
    .select({
      profissional: profissionais.nome,
      especialidade: especialidades.nome,
      diaSemana: disponibilidade.diaSemana,
      horarioInicio: disponibilidade.horarioInicio,
      horarioFim: disponibilidade.horarioFim,
      duracaoSlotMinutos: disponibilidade.duracaoSlotMinutos,
      vagasPorSlot: disponibilidade.vagasPorSlot,
    })
    .from(disponibilidade)
    .innerJoin(profissionais, eq(disponibilidade.profissionalId, profissionais.id))
    .innerJoin(especialidades, eq(profissionais.especialidadeId, especialidades.id))
    .where(condicoes.length ? and(...condicoes) : undefined);
}

export async function registrarConversa(
  sessionId: string,
  pergunta: string,
  resposta: string,
  canal: "mysql" | "ia"
) {
  await db.insert(conversas).values({ sessionId, pergunta, resposta, canal });
}

export async function buscarHistoricoConversa(sessionId: string) {
  const linhas = await db
    .select({ pergunta: conversas.pergunta, resposta: conversas.resposta })
    .from(conversas)
    .where(eq(conversas.sessionId, sessionId))
    .orderBy(desc(conversas.criadoEm))
    .limit(LIMITE_HISTORICO);

  // veio mais recente -> mais antiga; inverte pra ordem cronologica antes
  // de mandar pro Ollama (senao a "conversa" fica de tras pra frente).
  return linhas.reverse();
}
