import { mysqlTable, int, varchar, mysqlEnum, time, text, timestamp } from "drizzle-orm/mysql-core";

// Espelha db/migration/V1__cria_grade_disponibilidade.sql (fonte de verdade
// do schema e' a migracao Flyway, nao o drizzle-kit - aqui e' so o mapeamento
// TS pra montar as queries).

export const especialidades = mysqlTable("especialidades", {
  id: int("id").autoincrement().primaryKey(),
  nome: varchar("nome", { length: 100 }).notNull(),
  descricaoCurta: varchar("descricao_curta", { length: 255 }).notNull(),
});

export const profissionais = mysqlTable("profissionais", {
  id: int("id").autoincrement().primaryKey(),
  nome: varchar("nome", { length: 150 }).notNull(),
  especialidadeId: int("especialidade_id").notNull(),
  anosExperiencia: int("anos_experiencia").notNull(),
});

export const disponibilidade = mysqlTable("disponibilidade", {
  id: int("id").autoincrement().primaryKey(),
  profissionalId: int("profissional_id").notNull(),
  diaSemana: mysqlEnum("dia_semana", ["segunda", "terca", "quarta", "quinta", "sexta"]).notNull(),
  horarioInicio: time("horario_inicio").notNull(),
  horarioFim: time("horario_fim").notNull(),
  duracaoSlotMinutos: int("duracao_slot_minutos").notNull().default(50),
  vagasPorSlot: int("vagas_por_slot").notNull().default(1),
});

export const conversas = mysqlTable("conversas", {
  id: int("id").autoincrement().primaryKey(),
  sessionId: varchar("session_id", { length: 64 }).notNull(),
  pergunta: text("pergunta").notNull(),
  resposta: text("resposta").notNull(),
  canal: mysqlEnum("canal", ["mysql", "ia"]).notNull(),
  criadoEm: timestamp("criado_em").notNull().defaultNow(),
});
