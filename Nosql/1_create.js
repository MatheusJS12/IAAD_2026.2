// CREATE: inserindo novos dados no Firestore.
const { db, titulo } = require("./conexao");

// No MySQL isso é feito pelo TRIGGER trg_resultado_valida_insert.
// No Firestore a validação fica no código da aplicação (ou nas Security Rules).
function validaResultado(r) {
  if (r.pontuacao < 0 || r.pontuacao > 100) throw new Error("Pontuação inválida: deve estar entre 0 e 100.");
  if (r.classificacao < 1) throw new Error("Classificação inválida: deve ser 1 ou maior.");
}

async function main() {
  titulo("CREATE 1 - nova equipe (set com ID escolhido)");
  await db.collection("equipes").doc("8").set({
    nome_equipe: "Boa Viagem Bots",
    escola: "Colégio Boa Viagem",
    cidade: "Recife",
  });
  console.log("Equipe 8 criada.");

  titulo("CREATE 2 - integrante dentro da SUBCOLEÇÃO da equipe 8");
  await db.collection("equipes").doc("8").collection("integrantes").doc("16").set({
    nome_integrante: "Beatriz Santos",
    funcao: "Capitão",
    data_nascimento: new Date("2008-05-10"),
    email: "beatriz.santos@email.com",
  });
  console.log("Integrante criado em equipes/8/integrantes/16.");

  titulo("CREATE 3 - novo robô, apontando para a equipe 8 (referência = FK)");
  await db.collection("robos").doc("13").set({
    nome_robo: "Maré Alta",
    categoria: "Sumô",
    data_criacao: new Date("2026-09-10"),
    equipe_id: "8",
  });
  console.log("Robô 13 criado.");

  titulo("CREATE 4 - novo resultado (ID composto prova + classificação, como a PK do MySQL)");
  const novo = { nome_prova: "Desafio Livre", classificacao: 5, pontuacao: 65.0, robo_id: "13", nome_robo: "Maré Alta" };
  validaResultado(novo);
  await db.collection("resultados").doc("desafio-livre_5").set(novo);
  console.log("Resultado desafio-livre_5 criado.");

  titulo("CREATE 5 - chave duplicada (equivale a violar a PRIMARY KEY)");
  try {
    // create() falha se o documento já existir
    await db.collection("resultados").doc("sumo-3kg_1").create({
      nome_prova: "Sumô 3kg", classificacao: 1, pontuacao: 50, robo_id: "1", nome_robo: "Caranguejo X",
    });
  } catch (e) {
    console.log("Erro esperado:", e.message);
  }

  titulo("CREATE 6 - dado inválido (o que o TRIGGER do MySQL bloquearia)");
  try {
    validaResultado({ nome_prova: "Resgate", classificacao: 4, pontuacao: 150, robo_id: "3" });
  } catch (e) {
    console.log("Bloqueado pela validação:", e.message);
  }
}

main().catch(console.error);
