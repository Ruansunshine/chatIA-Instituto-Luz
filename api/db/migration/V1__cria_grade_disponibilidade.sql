-- ============================================================
-- Trabalho: Base de Conhecimento com IA Generativa (Sistemas Inteligentes)
-- Grade de disponibilidade do Instituto Luz - dado ficticio pra fins academicos.
-- Especialidades e profissionais sao reais (extraidos do sistema SmartClinic
-- em 16/09/2026); apenas a grade de dia/horario e ficticia, ja que o sistema
-- real nao modela disponibilidade em grade fixa.
-- ============================================================

CREATE TABLE especialidades (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nome VARCHAR(100) NOT NULL,
  descricao_curta VARCHAR(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE profissionais (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nome VARCHAR(150) NOT NULL,
  especialidade_id INT NOT NULL,
  anos_experiencia INT NOT NULL,
  CONSTRAINT fk_profissionais_especialidade
    FOREIGN KEY (especialidade_id) REFERENCES especialidades(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE disponibilidade (
  id INT AUTO_INCREMENT PRIMARY KEY,
  profissional_id INT NOT NULL,
  dia_semana ENUM('segunda','terca','quarta','quinta','sexta') NOT NULL,
  horario_inicio TIME NOT NULL,
  horario_fim TIME NOT NULL,
  duracao_slot_minutos INT NOT NULL DEFAULT 50,
  vagas_por_slot INT NOT NULL DEFAULT 1,
  CONSTRAINT fk_disponibilidade_profissional
    FOREIGN KEY (profissional_id) REFERENCES profissionais(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- especialidades (7 reais, extraidas do cadastro do SmartClinic)
INSERT INTO especialidades (nome, descricao_curta) VALUES
  ('Pilates', 'Fortalecimento, flexibilidade e equilibrio corporal'),
  ('Osteopatia', 'Avaliacao e tratamento manual de restricoes de mobilidade'),
  ('Fisioterapia respiratoria', 'Tratamento de questoes respiratorias'),
  ('Traumato ortopedia e esportiva', 'Reabilitacao de lesoes ortopedicas e esportivas'),
  ('Fisioterapia em traumatologia e esporte', 'Acompanhamento de lesoes relacionadas ao esporte, sem profissional ativo no momento'),
  ('Assimetria craniana', 'Avaliacao e acompanhamento de assimetrias cranianas em bebes, sem profissional ativo no momento'),
  ('Injetaveis', 'Procedimentos injetaveis complementares ao tratamento fisioterapeutico, sem profissional ativo no momento');

-- profissionais (7 reais, extraidos do sistema SmartClinic em 16/09/2026)
INSERT INTO profissionais (nome, especialidade_id, anos_experiencia) VALUES
  ('Fernanda de Sousa Negreiros',    (SELECT id FROM especialidades WHERE nome = 'Traumato ortopedia e esportiva'), 6),
  ('Amorim Da Silva De Menezes',     (SELECT id FROM especialidades WHERE nome = 'Fisioterapia respiratoria'), 9),
  ('Antonio Mateus da Silva Aguiar', (SELECT id FROM especialidades WHERE nome = 'Osteopatia'), 5),
  ('Beatriz Da Luz Sousa Lima',      (SELECT id FROM especialidades WHERE nome = 'Osteopatia'), 7),
  ('Guimaraes Sousa Costa Rayanne',  (SELECT id FROM especialidades WHERE nome = 'Osteopatia'), 4),
  ('Ana Livia Silva De Sousa',       (SELECT id FROM especialidades WHERE nome = 'Pilates'), 8),
  ('Luan Eduardo Oliveira da Silva', (SELECT id FROM especialidades WHERE nome = 'Pilates'), 3);

-- disponibilidade (ficticia - dias/horarios variados dentro da janela real 08:00-18:00, seg-sex)
INSERT INTO disponibilidade (profissional_id, dia_semana, horario_inicio, horario_fim, duracao_slot_minutos, vagas_por_slot)
SELECT id, 'segunda', '08:00:00', '12:00:00', 50, 1 FROM profissionais WHERE nome = 'Fernanda de Sousa Negreiros'
UNION ALL SELECT id, 'quarta',  '08:00:00', '12:00:00', 50, 1 FROM profissionais WHERE nome = 'Fernanda de Sousa Negreiros'
UNION ALL SELECT id, 'sexta',   '08:00:00', '12:00:00', 50, 1 FROM profissionais WHERE nome = 'Fernanda de Sousa Negreiros'

UNION ALL SELECT id, 'terca',   '13:00:00', '18:00:00', 50, 1 FROM profissionais WHERE nome = 'Amorim Da Silva De Menezes'
UNION ALL SELECT id, 'quinta',  '13:00:00', '18:00:00', 50, 1 FROM profissionais WHERE nome = 'Amorim Da Silva De Menezes'

UNION ALL SELECT id, 'segunda', '08:00:00', '13:00:00', 50, 1 FROM profissionais WHERE nome = 'Antonio Mateus da Silva Aguiar'
UNION ALL SELECT id, 'terca',   '08:00:00', '13:00:00', 50, 1 FROM profissionais WHERE nome = 'Antonio Mateus da Silva Aguiar'
UNION ALL SELECT id, 'quinta',  '08:00:00', '13:00:00', 50, 1 FROM profissionais WHERE nome = 'Antonio Mateus da Silva Aguiar'

UNION ALL SELECT id, 'segunda', '13:00:00', '18:00:00', 50, 1 FROM profissionais WHERE nome = 'Beatriz Da Luz Sousa Lima'
UNION ALL SELECT id, 'quarta',  '13:00:00', '18:00:00', 50, 1 FROM profissionais WHERE nome = 'Beatriz Da Luz Sousa Lima'
UNION ALL SELECT id, 'sexta',   '13:00:00', '18:00:00', 50, 1 FROM profissionais WHERE nome = 'Beatriz Da Luz Sousa Lima'

UNION ALL SELECT id, 'terca',   '08:00:00', '12:00:00', 50, 1 FROM profissionais WHERE nome = 'Guimaraes Sousa Costa Rayanne'
UNION ALL SELECT id, 'quinta',  '08:00:00', '12:00:00', 50, 1 FROM profissionais WHERE nome = 'Guimaraes Sousa Costa Rayanne'
UNION ALL SELECT id, 'sexta',   '08:00:00', '12:00:00', 50, 1 FROM profissionais WHERE nome = 'Guimaraes Sousa Costa Rayanne'

UNION ALL SELECT id, 'segunda', '08:00:00', '11:00:00', 50, 2 FROM profissionais WHERE nome = 'Ana Livia Silva De Sousa'
UNION ALL SELECT id, 'terca',   '08:00:00', '11:00:00', 50, 2 FROM profissionais WHERE nome = 'Ana Livia Silva De Sousa'
UNION ALL SELECT id, 'quarta',  '08:00:00', '11:00:00', 50, 2 FROM profissionais WHERE nome = 'Ana Livia Silva De Sousa'
UNION ALL SELECT id, 'quinta',  '08:00:00', '11:00:00', 50, 2 FROM profissionais WHERE nome = 'Ana Livia Silva De Sousa'
UNION ALL SELECT id, 'sexta',   '08:00:00', '11:00:00', 50, 2 FROM profissionais WHERE nome = 'Ana Livia Silva De Sousa'

UNION ALL SELECT id, 'segunda', '14:00:00', '18:00:00', 50, 1 FROM profissionais WHERE nome = 'Luan Eduardo Oliveira da Silva'
UNION ALL SELECT id, 'quarta',  '14:00:00', '18:00:00', 50, 1 FROM profissionais WHERE nome = 'Luan Eduardo Oliveira da Silva'
UNION ALL SELECT id, 'sexta',   '14:00:00', '18:00:00', 50, 1 FROM profissionais WHERE nome = 'Luan Eduardo Oliveira da Silva';
