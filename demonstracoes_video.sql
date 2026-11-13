-- =====================================================================
-- Roteiro de comandos para o vídeo (FKs, cascata, trigger, procedure)
-- Rodar DEPOIS do torneio_robotica.sql. Os comandos que dão erro
-- estão marcados com "ESPERADO: ERRO" e são de propósito.
-- =====================================================================

USE torneio_robotica;

-- ---------------------------------------------------------------------
-- A) VIOLAÇÃO DE INTEGRIDADE REFERENCIAL
-- ---------------------------------------------------------------------

-- Robô apontando para uma equipe que não existe (id 999)
-- ESPERADO: ERRO 1452 (Cannot add or update a child row: a foreign key constraint fails)
INSERT INTO robo (nome_robo, categoria, data_criacao, id_equipe)
VALUES ('Robô Fantasma', 'Sumô', '2026-01-01', 999);

-- Resultado para um robô que não existe
-- ESPERADO: ERRO 1452
INSERT INTO resultado (nome_prova, classificacao, pontuacao, id_robo)
VALUES ('Sumô 3kg', 4, 50.00, 999);

-- ---------------------------------------------------------------------
-- B) ATUALIZAÇÃO EM CASCATA (ON UPDATE CASCADE)
-- Muda o id da equipe 1 para 100: os robôs e integrantes dela
-- passam a apontar para 100 automaticamente.
-- ---------------------------------------------------------------------

SELECT id_robo, nome_robo, id_equipe FROM robo WHERE id_equipe = 1;
SELECT nome_integrante, id_equipe FROM integrante WHERE id_equipe = 1;

UPDATE equipe SET id_equipe = 100 WHERE id_equipe = 1;

SELECT id_robo, nome_robo, id_equipe FROM robo WHERE id_equipe = 100;
SELECT nome_integrante, id_equipe FROM integrante WHERE id_equipe = 100;

-- ---------------------------------------------------------------------
-- C) REMOÇÃO EM CASCATA (ON DELETE CASCADE)
-- Apagar a equipe 5 (Petrolina Robotics) apaga também os robôs dela,
-- os resultados desses robôs e os integrantes da equipe.
-- ---------------------------------------------------------------------

SELECT COUNT(*) AS robos       FROM robo       WHERE id_equipe = 5;
SELECT COUNT(*) AS resultados  FROM resultado  WHERE id_robo IN (9, 10);
SELECT COUNT(*) AS integrantes FROM integrante WHERE id_equipe = 5;

DELETE FROM equipe WHERE id_equipe = 5;

SELECT COUNT(*) AS robos       FROM robo       WHERE id_equipe = 5;       -- 0
SELECT COUNT(*) AS resultados  FROM resultado  WHERE id_robo IN (9, 10);  -- 0
SELECT COUNT(*) AS integrantes FROM integrante WHERE id_equipe = 5;       -- 0

-- ---------------------------------------------------------------------
-- D) TRIGGER EM AÇÃO
-- ---------------------------------------------------------------------

-- Pontuação acima de 100
-- ESPERADO: ERRO 1644 'Pontuação inválida: deve estar entre 0 e 100.'
INSERT INTO resultado (nome_prova, classificacao, pontuacao, id_robo)
VALUES ('Mini Sumô', 3, 150.00, 12);

-- Classificação zero
-- ESPERADO: ERRO 1644 'Classificação inválida: deve ser 1 ou maior.'
INSERT INTO resultado (nome_prova, classificacao, pontuacao, id_robo)
VALUES ('Mini Sumô', 0, 60.00, 12);

-- Update com pontuação negativa (trigger de UPDATE)
-- ESPERADO: ERRO 1644
UPDATE resultado SET pontuacao = -5 WHERE nome_prova = 'Resgate' AND classificacao = 1;

-- Robô com data de criação no futuro
INSERT INTO robo (nome_robo, categoria, data_criacao, id_equipe)
VALUES ('Protótipo 2030', 'Sumô', '2030-01-01', 2);
-- ESPERADO: ERRO 1644 'Robô com data de criação futura não pode ter resultado.'
INSERT INTO resultado (nome_prova, classificacao, pontuacao, id_robo)
VALUES ('Sumô 3kg', 4, 60.00, LAST_INSERT_ID());

-- Inserção válida (passa pela trigger normalmente)
INSERT INTO resultado (nome_prova, classificacao, pontuacao, id_robo)
VALUES ('Mini Sumô', 3, 68.40, 12);

-- ---------------------------------------------------------------------
-- E) STORED PROCEDURE (bônus)
-- ---------------------------------------------------------------------

CALL sp_ranking_prova('Seguidor de Linha');
CALL sp_ranking_prova('Desafio Livre');

-- ---------------------------------------------------------------------
-- F) CONSULTAS NÃO TRIVIAIS
-- ---------------------------------------------------------------------

SELECT * FROM vw_desempenho_equipe ORDER BY pontuacao_total DESC;
SELECT * FROM vw_robos_sem_resultado;
SELECT * FROM vw_idade_robos ORDER BY idade_dias DESC;
SELECT * FROM vw_robos_por_mes ORDER BY mes;
SELECT * FROM vw_estatisticas_categoria;
SELECT * FROM vw_integrantes_equipe;
