-- Sem session_id o log de conversa era so auditoria (nunca lido de volta).
-- Com session_id, o Node consegue buscar as ultimas trocas da MESMA sessao
-- do navegador e mandar como historico pro Ollama - viabiliza follow-up
-- ("e o preco da segunda?" depois de perguntar sobre especialidades).
ALTER TABLE conversas
  ADD COLUMN session_id VARCHAR(64) NOT NULL DEFAULT '' AFTER id;

CREATE INDEX idx_conversas_session ON conversas (session_id, criado_em);
