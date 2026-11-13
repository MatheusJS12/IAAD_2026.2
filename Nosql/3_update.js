// UPDATE: alterando dados existentes.
const { db, titulo } = require("./conexao");

async function main() {
  titulo("UPDATE 1 - corrigir a pontuação de um resultado");
  const refRes = db.collection("resultados").doc("sumo-3kg_2");
  console.log("Antes: ", (await refRes.get()).data().pontuacao);
  await refRes.update({ pontuacao: 90.0 }); // altera só o campo informado
  console.log("Depois:", (await refRes.get()).data().pontuacao);

  titulo("UPDATE 2 - mudar a função de um integrante (documento dentro da subcoleção)");
  const refInt = db.collection("equipes").doc("1").collection("integrantes").doc("2");
  console.log("Antes: ", (await refInt.get()).data().funcao);
  await refInt.update({ funcao: "Mecânico" });
  console.log("Depois:", (await refInt.get()).data().funcao);

  titulo("UPDATE 3 - renomear um robô (e atualizar as cópias nos resultados)");
  // No MySQL o nome fica só na tabela robo e o JOIN sempre mostra o valor atual.
  // No Firestore o nome foi COPIADO para os resultados, então precisamos atualizar também.
  await db.collection("robos").doc("1").update({ nome_robo: "Caranguejo X2" });

  const copias = await db.collection("resultados").where("robo_id", "==", "1").get();
  const batch = db.batch();
  copias.docs.forEach((d) => batch.update(d.ref, { nome_robo: "Caranguejo X2" }));
  await batch.commit();
  console.log(`Robô renomeado e ${copias.size} cópias atualizadas nos resultados.`);
}

main().catch(console.error);
