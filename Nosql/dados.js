// Dados do Torneio de Robótica (os mesmos do torneio_robotica.sql do MySQL).

const equipes = [
  { id: "1", nome_equipe: "RoboRecife",         escola: "IFPE Campus Recife",                   cidade: "Recife" },
  { id: "2", nome_equipe: "Mangue Bots",        escola: "Escola Técnica Estadual Cícero Dias",  cidade: "Recife" },
  { id: "3", nome_equipe: "Olinda Tech",        escola: "EREM Olinda",                          cidade: "Olinda" },
  { id: "4", nome_equipe: "Caruaru Makers",     escola: "IFPE Campus Caruaru",                  cidade: "Caruaru" },
  { id: "5", nome_equipe: "Petrolina Robotics", escola: "IF Sertão Campus Petrolina",           cidade: "Petrolina" },
  { id: "6", nome_equipe: "Jaboatão Mecatron",  escola: "ETE Jaboatão dos Guararapes",          cidade: "Jaboatão dos Guararapes" },
  { id: "7", nome_equipe: "Garanhuns Volts",    escola: "IFPE Campus Garanhuns",                cidade: "Garanhuns" },
];

const robos = [
  { id: "1",  nome_robo: "Caranguejo X",   categoria: "Sumô",              data_criacao: new Date("2025-08-10"), equipe_id: "1" },
  { id: "2",  nome_robo: "Frevo Runner",   categoria: "Seguidor de Linha", data_criacao: new Date("2025-11-02"), equipe_id: "1" },
  { id: "3",  nome_robo: "Maracatu Bot",   categoria: "Resgate",           data_criacao: new Date("2026-02-15"), equipe_id: "2" },
  { id: "4",  nome_robo: "Mangue Speed",   categoria: "Seguidor de Linha", data_criacao: new Date("2025-09-20"), equipe_id: "2" },
  { id: "5",  nome_robo: "Alto da Sé",     categoria: "Sumô",              data_criacao: new Date("2026-01-12"), equipe_id: "3" },
  { id: "6",  nome_robo: "Bonecão",        categoria: "Mini Sumô",         data_criacao: new Date("2026-03-05"), equipe_id: "3" },
  { id: "7",  nome_robo: "Forró Tracker",  categoria: "Seguidor de Linha", data_criacao: new Date("2025-07-30"), equipe_id: "4" },
  { id: "8",  nome_robo: "Agreste Rescue", categoria: "Resgate",           data_criacao: new Date("2026-04-18"), equipe_id: "4" },
  { id: "9",  nome_robo: "Velho Chico",    categoria: "Sumô",              data_criacao: new Date("2025-10-08"), equipe_id: "5" },
  { id: "10", nome_robo: "Sertão Mini",    categoria: "Mini Sumô",         data_criacao: new Date("2026-05-22"), equipe_id: "5" },
  { id: "11", nome_robo: "Guararapes",     categoria: "Resgate",           data_criacao: new Date("2026-06-01"), equipe_id: "6" },
  { id: "12", nome_robo: "Friozinho",      categoria: "Mini Sumô",         data_criacao: new Date("2026-08-14"), equipe_id: "7" }, // sem resultado
];

const resultados = [
  { nome_prova: "Sumô 3kg",          classificacao: 1, pontuacao: 95.5,  robo_id: "9"  },
  { nome_prova: "Sumô 3kg",          classificacao: 2, pontuacao: 88.0,  robo_id: "1"  },
  { nome_prova: "Sumô 3kg",          classificacao: 3, pontuacao: 72.25, robo_id: "5"  },
  { nome_prova: "Seguidor de Linha", classificacao: 1, pontuacao: 98.75, robo_id: "7"  },
  { nome_prova: "Seguidor de Linha", classificacao: 2, pontuacao: 91.3,  robo_id: "2"  },
  { nome_prova: "Seguidor de Linha", classificacao: 3, pontuacao: 84.1,  robo_id: "4"  },
  { nome_prova: "Resgate",           classificacao: 1, pontuacao: 89.4,  robo_id: "3"  },
  { nome_prova: "Resgate",           classificacao: 2, pontuacao: 81.0,  robo_id: "8"  },
  { nome_prova: "Resgate",           classificacao: 3, pontuacao: 65.75, robo_id: "11" },
  { nome_prova: "Mini Sumô",         classificacao: 1, pontuacao: 90.0,  robo_id: "10" },
  { nome_prova: "Mini Sumô",         classificacao: 2, pontuacao: 77.5,  robo_id: "6"  },
  { nome_prova: "Desafio Livre",     classificacao: 1, pontuacao: 93.2,  robo_id: "3"  },
  { nome_prova: "Desafio Livre",     classificacao: 2, pontuacao: 86.6,  robo_id: "1"  },
  { nome_prova: "Desafio Livre",     classificacao: 3, pontuacao: 79.9,  robo_id: "7"  },
  { nome_prova: "Desafio Livre",     classificacao: 4, pontuacao: 70.0,  robo_id: "9"  },
];

// Cada integrante vira um documento na SUBCOLEÇÃO equipes/{equipe_id}/integrantes
const integrantes = [
  { id: "1",  nome_integrante: "Ana Beatriz Lima",     funcao: "Capitão",     data_nascimento: new Date("2008-03-14"), email: "ana.lima@email.com",         equipe_id: "1" },
  { id: "2",  nome_integrante: "Pedro Henrique Souza", funcao: "Programador", data_nascimento: new Date("2007-11-02"), email: "pedro.souza@email.com",      equipe_id: "1" },
  { id: "3",  nome_integrante: "Carlos Alberto Melo",  funcao: "Mentor",      data_nascimento: new Date("1985-06-20"), email: "carlos.melo@email.com",      equipe_id: "1" },
  { id: "4",  nome_integrante: "Júlia Cavalcanti",     funcao: "Capitão",     data_nascimento: new Date("2009-01-25"), email: "julia.cavalcanti@email.com", equipe_id: "2" },
  { id: "5",  nome_integrante: "Rafael Barbosa",       funcao: "Mecânico",    data_nascimento: new Date("2008-07-09"), email: "rafael.barbosa@email.com",   equipe_id: "2" },
  { id: "6",  nome_integrante: "Larissa Moura",        funcao: "Programador", data_nascimento: new Date("2008-12-30"), email: "larissa.moura@email.com",    equipe_id: "3" },
  { id: "7",  nome_integrante: "Thiago Nascimento",    funcao: "Eletrônica",  data_nascimento: new Date("2007-05-17"), email: "thiago.n@email.com",         equipe_id: "3" },
  { id: "8",  nome_integrante: "Mariana Albuquerque",  funcao: "Capitão",     data_nascimento: new Date("2008-09-11"), email: "mariana.alb@email.com",      equipe_id: "4" },
  { id: "9",  nome_integrante: "Lucas Ferreira",       funcao: "Programador", data_nascimento: new Date("2009-04-03"), email: "lucas.ferreira@email.com",   equipe_id: "4" },
  { id: "10", nome_integrante: "José Cícero Santos",   funcao: "Mentor",      data_nascimento: new Date("1979-02-28"), email: "jose.cicero@email.com",      equipe_id: "4" },
  { id: "11", nome_integrante: "Gabriela Rocha",       funcao: "Capitão",     data_nascimento: new Date("2007-08-21"), email: "gabriela.rocha@email.com",   equipe_id: "5" },
  { id: "12", nome_integrante: "Matheus Araújo",       funcao: "Mecânico",    data_nascimento: new Date("2008-10-15"), email: "matheus.araujo@email.com",   equipe_id: "5" },
  { id: "13", nome_integrante: "Isabela Torres",       funcao: "Programador", data_nascimento: new Date("2009-06-06"), email: "isabela.torres@email.com",   equipe_id: "6" },
  { id: "14", nome_integrante: "Felipe Andrade",       funcao: "Eletrônica",  data_nascimento: new Date("2008-02-19"), email: "felipe.andrade@email.com",   equipe_id: "6" },
  { id: "15", nome_integrante: "Camila Pereira",       funcao: "Capitão",     data_nascimento: new Date("2009-11-27"), email: "camila.pereira@email.com",   equipe_id: "7" },
];

// No MySQL a PK do resultado é composta (nome_prova, classificacao).
// No Firestore reproduzimos isso no ID do documento: "sumo-3kg_1", "resgate_2"...
const slug = (t) =>
  t.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "");
const idResultado = (r) => `${slug(r.nome_prova)}_${r.classificacao}`;

module.exports = { equipes, robos, resultados, integrantes, slug, idResultado };
