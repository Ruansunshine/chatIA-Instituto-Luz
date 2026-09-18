-- Log de auditoria de cada pergunta/resposta do chat - nao e' RAG nem input
-- do modelo, so historico pra evidencia de uso e debug (canal indica se foi
-- resolvido direto no MySQL ou repassado pra IA via Ollama).
CREATE TABLE conversas (
  id INT AUTO_INCREMENT PRIMARY KEY,
  pergunta TEXT NOT NULL,
  resposta TEXT NOT NULL,
  canal ENUM('mysql', 'ia') NOT NULL,
  criado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
