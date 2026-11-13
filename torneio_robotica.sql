-- =====================================================================
-- IAAD 2026.2 - 2ª VA - Atividade 1
-- Banco de Dados: Torneio de Robótica (MySQL 8)
-- Script de criação e carga
--
-- Tabelas: equipe, robo, resultado (dadas no DER)
--          integrante (nova tabela criada pela equipe)
-- Extras:  trigger de validação, stored procedure (bônus) e views
--          com as consultas não triviais usadas no dashboard
-- =====================================================================

DROP DATABASE IF EXISTS torneio_robotica;
CREATE DATABASE torneio_robotica
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE torneio_robotica;

-- ---------------------------------------------------------------------
-- 1. CRIAÇÃO DAS TABELAS
-- ---------------------------------------------------------------------

CREATE TABLE equipe (
  id_equipe    INT          NOT NULL AUTO_INCREMENT,
  nome_equipe  VARCHAR(100) NOT NULL,
  escola       VARCHAR(100) NOT NULL,
  cidade       VARCHAR(80)  NOT NULL,
  PRIMARY KEY (id_equipe),
  UNIQUE KEY uq_equipe_nome (nome_equipe)
) ENGINE = InnoDB;

CREATE TABLE robo (
  id_robo       INT          NOT NULL AUTO_INCREMENT,
  nome_robo     VARCHAR(100) NOT NULL,
  categoria     VARCHAR(50)  NOT NULL,
  data_criacao  DATE         NOT NULL,
  id_equipe     INT          NOT NULL,
  PRIMARY KEY (id_robo),
  KEY fk_robo_equipe_idx (id_equipe),
  CONSTRAINT fk_robo_equipe
    FOREIGN KEY (id_equipe) REFERENCES equipe (id_equipe)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE = InnoDB;

-- PK composta (nome_prova, classificacao), conforme o DER:
-- em cada prova só existe um 1º lugar, um 2º lugar etc.
CREATE TABLE resultado (
  nome_prova     VARCHAR(100) NOT NULL,
  classificacao  INT          NOT NULL,
  pontuacao      DECIMAL(6,2) NOT NULL,
  id_robo        INT          NOT NULL,
  PRIMARY KEY (nome_prova, classificacao),
  KEY fk_resultado_robo_idx (id_robo),
  CONSTRAINT fk_resultado_robo
    FOREIGN KEY (id_robo) REFERENCES robo (id_robo)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE = InnoDB;

-- Nova tabela (escolha da equipe): integrantes de cada equipe.
-- Relacionamento 1:N com equipe (uma equipe tem vários integrantes).
CREATE TABLE integrante (
  id_integrante    INT          NOT NULL AUTO_INCREMENT,
  nome_integrante  VARCHAR(100) NOT NULL,
  funcao           VARCHAR(50)  NOT NULL,   -- Capitão, Programador, Mecânico, Eletrônica, Mentor
  data_nascimento  DATE         NOT NULL,
  email            VARCHAR(100) NULL,
  id_equipe        INT          NOT NULL,
  PRIMARY KEY (id_integrante),
  UNIQUE KEY uq_integrante_email (email),
  KEY fk_integrante_equipe_idx (id_equipe),
  CONSTRAINT fk_integrante_equipe
    FOREIGN KEY (id_equipe) REFERENCES equipe (id_equipe)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE = InnoDB;

-- ---------------------------------------------------------------------
-- 2. TRIGGERS
-- Valida os dados de resultado antes de inserir ou atualizar:
--   * pontuação deve ficar entre 0 e 100
--   * classificação deve ser 1 ou maior
--   * o robô não pode ter sido criado depois de hoje (não faz sentido
--     um robô "do futuro" ter resultado em prova)
-- Se alguma regra for violada, a operação é cancelada com SIGNAL.
-- ---------------------------------------------------------------------

DELIMITER $$

CREATE TRIGGER trg_resultado_valida_insert
BEFORE INSERT ON resultado
FOR EACH ROW
BEGIN
  DECLARE v_data_criacao DATE;

  IF NEW.pontuacao < 0 OR NEW.pontuacao > 100 THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Pontuação inválida: deve estar entre 0 e 100.';
  END IF;

  IF NEW.classificacao < 1 THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Classificação inválida: deve ser 1 ou maior.';
  END IF;

  SELECT data_criacao INTO v_data_criacao
    FROM robo WHERE id_robo = NEW.id_robo;

  IF v_data_criacao > CURDATE() THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Robô com data de criação futura não pode ter resultado.';
  END IF;
END$$

CREATE TRIGGER trg_resultado_valida_update
BEFORE UPDATE ON resultado
FOR EACH ROW
BEGIN
  IF NEW.pontuacao < 0 OR NEW.pontuacao > 100 THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Pontuação inválida: deve estar entre 0 e 100.';
  END IF;

  IF NEW.classificacao < 1 THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Classificação inválida: deve ser 1 ou maior.';
  END IF;
END$$

-- ---------------------------------------------------------------------
-- 3. STORED PROCEDURE (bonificação extra)
-- Retorna o ranking de uma prova com robô, equipe e escola.
-- Uso: CALL sp_ranking_prova('Sumô 3kg');
-- ---------------------------------------------------------------------

CREATE PROCEDURE sp_ranking_prova(IN p_nome_prova VARCHAR(100))
BEGIN
  SELECT r.classificacao,
         ro.nome_robo,
         e.nome_equipe,
         e.escola,
         r.pontuacao
    FROM resultado r
    JOIN robo   ro ON ro.id_robo  = r.id_robo
    JOIN equipe e  ON e.id_equipe = ro.id_equipe
   WHERE r.nome_prova = p_nome_prova
   ORDER BY r.classificacao;
END$$

DELIMITER ;

-- ---------------------------------------------------------------------
-- 4. CARGA DE DADOS
-- ---------------------------------------------------------------------

INSERT INTO equipe (nome_equipe, escola, cidade) VALUES
  ('RoboRecife',       'IFPE Campus Recife',               'Recife'),
  ('Mangue Bots',      'Escola Técnica Estadual Cícero Dias', 'Recife'),
  ('Olinda Tech',      'EREM Olinda',                       'Olinda'),
  ('Caruaru Makers',   'IFPE Campus Caruaru',               'Caruaru'),
  ('Petrolina Robotics','IF Sertão Campus Petrolina',       'Petrolina'),
  ('Jaboatão Mecatron', 'ETE Jaboatão dos Guararapes',      'Jaboatão dos Guararapes'),
  ('Garanhuns Volts',  'IFPE Campus Garanhuns',             'Garanhuns');

INSERT INTO robo (nome_robo, categoria, data_criacao, id_equipe) VALUES
  ('Caranguejo X',  'Sumô',              '2025-08-10', 1),  -- 1
  ('Frevo Runner',  'Seguidor de Linha', '2025-11-02', 1),  -- 2
  ('Maracatu Bot',  'Resgate',           '2026-02-15', 2),  -- 3
  ('Mangue Speed',  'Seguidor de Linha', '2025-09-20', 2),  -- 4
  ('Alto da Sé',    'Sumô',              '2026-01-12', 3),  -- 5
  ('Bonecão',       'Mini Sumô',         '2026-03-05', 3),  -- 6
  ('Forró Tracker', 'Seguidor de Linha', '2025-07-30', 4),  -- 7
  ('Agreste Rescue','Resgate',           '2026-04-18', 4),  -- 8
  ('Velho Chico',   'Sumô',              '2025-10-08', 5),  -- 9
  ('Sertão Mini',   'Mini Sumô',         '2026-05-22', 5),  -- 10
  ('Guararapes',    'Resgate',           '2026-06-01', 6),  -- 11
  ('Friozinho',     'Mini Sumô',         '2026-08-14', 7);  -- 12 (sem resultado)

INSERT INTO resultado (nome_prova, classificacao, pontuacao, id_robo) VALUES
  -- Sumô 3kg
  ('Sumô 3kg', 1, 95.50, 9),
  ('Sumô 3kg', 2, 88.00, 1),
  ('Sumô 3kg', 3, 72.25, 5),
  -- Seguidor de Linha
  ('Seguidor de Linha', 1, 98.75, 7),
  ('Seguidor de Linha', 2, 91.30, 2),
  ('Seguidor de Linha', 3, 84.10, 4),
  -- Resgate
  ('Resgate', 1, 89.40, 3),
  ('Resgate', 2, 81.00, 8),
  ('Resgate', 3, 65.75, 11),
  -- Mini Sumô
  ('Mini Sumô', 1, 90.00, 10),
  ('Mini Sumô', 2, 77.50, 6),
  -- Desafio Livre (aberto a qualquer categoria)
  ('Desafio Livre', 1, 93.20, 3),
  ('Desafio Livre', 2, 86.60, 1),
  ('Desafio Livre', 3, 79.90, 7),
  ('Desafio Livre', 4, 70.00, 9);

INSERT INTO integrante (nome_integrante, funcao, data_nascimento, email, id_equipe) VALUES
  ('Ana Beatriz Lima',      'Capitão',     '2008-03-14', 'ana.lima@email.com',        1),
  ('Pedro Henrique Souza',  'Programador', '2007-11-02', 'pedro.souza@email.com',     1),
  ('Carlos Alberto Melo',   'Mentor',      '1985-06-20', 'carlos.melo@email.com',     1),
  ('Júlia Cavalcanti',      'Capitão',     '2009-01-25', 'julia.cavalcanti@email.com',2),
  ('Rafael Barbosa',        'Mecânico',    '2008-07-09', 'rafael.barbosa@email.com',  2),
  ('Larissa Moura',         'Programador', '2008-12-30', 'larissa.moura@email.com',   3),
  ('Thiago Nascimento',     'Eletrônica',  '2007-05-17', 'thiago.n@email.com',        3),
  ('Mariana Albuquerque',   'Capitão',     '2008-09-11', 'mariana.alb@email.com',     4),
  ('Lucas Ferreira',        'Programador', '2009-04-03', 'lucas.ferreira@email.com',  4),
  ('José Cícero Santos',    'Mentor',      '1979-02-28', 'jose.cicero@email.com',     4),
  ('Gabriela Rocha',        'Capitão',     '2007-08-21', 'gabriela.rocha@email.com',  5),
  ('Matheus Araújo',        'Mecânico',    '2008-10-15', 'matheus.araujo@email.com',  5),
  ('Isabela Torres',        'Programador', '2009-06-06', 'isabela.torres@email.com',  6),
  ('Felipe Andrade',        'Eletrônica',  '2008-02-19', 'felipe.andrade@email.com',  6),
  ('Camila Pereira',        'Capitão',     '2009-11-27', 'camila.pereira@email.com',  7);

-- ---------------------------------------------------------------------
-- 5. CONSULTAS NÃO TRIVIAIS (como VIEWs, prontas para o dashboard)
-- ---------------------------------------------------------------------

-- 5.1 Desempenho por equipe: JOIN + GROUP BY + SUM/AVG/COUNT/MAX
CREATE VIEW vw_desempenho_equipe AS
SELECT e.id_equipe,
       e.nome_equipe,
       e.cidade,
       COUNT(r.nome_prova)              AS qtd_participacoes,
       COALESCE(SUM(r.pontuacao), 0)    AS pontuacao_total,
       ROUND(AVG(r.pontuacao), 2)       AS pontuacao_media,
       MAX(r.pontuacao)                 AS melhor_pontuacao,
       COALESCE(SUM(r.classificacao = 1), 0) AS qtd_primeiros_lugares
  FROM equipe e
  LEFT JOIN robo ro     ON ro.id_equipe = e.id_equipe
  LEFT JOIN resultado r ON r.id_robo    = ro.id_robo
 GROUP BY e.id_equipe, e.nome_equipe, e.cidade;

-- 5.2 LEFT JOIN exclusiva: robôs que ainda não têm nenhum resultado
CREATE VIEW vw_robos_sem_resultado AS
SELECT ro.id_robo, ro.nome_robo, ro.categoria, e.nome_equipe
  FROM robo ro
  JOIN equipe e         ON e.id_equipe = ro.id_equipe
  LEFT JOIN resultado r ON r.id_robo   = ro.id_robo
 WHERE r.id_robo IS NULL;

-- 5.3 Manipulação de datas: idade de cada robô (em dias e meses)
CREATE VIEW vw_idade_robos AS
SELECT ro.nome_robo,
       ro.categoria,
       e.nome_equipe,
       DATE_FORMAT(ro.data_criacao, '%d/%m/%Y')              AS criado_em,
       DATEDIFF(CURDATE(), ro.data_criacao)                  AS idade_dias,
       TIMESTAMPDIFF(MONTH, ro.data_criacao, CURDATE())      AS idade_meses
  FROM robo ro
  JOIN equipe e ON e.id_equipe = ro.id_equipe;

-- 5.4 Robôs criados por mês (datas + agregação), bom para gráfico de linha
CREATE VIEW vw_robos_por_mes AS
SELECT DATE_FORMAT(data_criacao, '%Y-%m') AS mes,
       COUNT(*)                            AS qtd_robos
  FROM robo
 GROUP BY DATE_FORMAT(data_criacao, '%Y-%m');

-- 5.5 Estatísticas por categoria de robô
CREATE VIEW vw_estatisticas_categoria AS
SELECT ro.categoria,
       COUNT(DISTINCT ro.id_robo)   AS qtd_robos,
       COUNT(r.nome_prova)          AS qtd_resultados,
       ROUND(AVG(r.pontuacao), 2)   AS media_pontuacao,
       MIN(r.pontuacao)             AS menor_pontuacao,
       MAX(r.pontuacao)             AS maior_pontuacao
  FROM robo ro
  LEFT JOIN resultado r ON r.id_robo = ro.id_robo
 GROUP BY ro.categoria;

-- 5.6 Faixa etária dos integrantes por equipe (datas + agregação)
CREATE VIEW vw_integrantes_equipe AS
SELECT e.nome_equipe,
       COUNT(i.id_integrante)                                        AS qtd_integrantes,
       ROUND(AVG(TIMESTAMPDIFF(YEAR, i.data_nascimento, CURDATE())), 1) AS idade_media
  FROM equipe e
  LEFT JOIN integrante i ON i.id_equipe = e.id_equipe
 GROUP BY e.nome_equipe;
