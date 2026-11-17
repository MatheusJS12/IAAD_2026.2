// DELETE: removendo dados e entendendo o que NÃO é automático no Firestore.
const { db, titulo } = require("./conexao");

async function main() {
  titulo("DELETE 1 - remover um resultado");
  await db.collection("resultados").doc("desafio-livre_4").delete();
  console.log("Resultado desafio-livre_4 removido.");

  titulo("DELETE 2 - remover a equipe 3 (Olinda Tech) SEM cascata");
  await db.collection("equipes").doc("3").delete();

  const orfaos = await db.collection("robos").where("equipe_id", "==", "3").get();
  const integ = await db.collection("equipes").doc("3").collection("integrantes").get();
  console.log(`Robôs que ainda apontam para a equipe 3: ${orfaos.size}`);
  console.log(`Integrantes que ainda existem na subcoleção da equipe 3: ${integ.size}`);
  console.log("=> No MySQL, o ON DELETE CASCADE teria apagado tudo isso automaticamente.");

  titulo("DELETE 3 - cascata MANUAL (feita pelo nosso código)");
  for (const robo of orfaos.docs) {
    const res = await db.collection("resultados").where("robo_id", "==", robo.id).get();
    for (const r of res.docs) await r.ref.delete(); // resultados do robô
    await robo.ref.delete();                        // o próprio robô
    console.log(`Robô ${robo.data().nome_robo} removido (com ${res.size} resultado(s)).`);
  }
  await db.recursiveDelete(db.collection("equipes").doc("3").collection("integrantes")); // subcoleção
  console.log("Subcoleção de integrantes da equipe 3 removida.");

  const restantes = await db.collection("robos").get();
  console.log(`Robôs restantes no banco: ${restantes.size}`);
}

main().catch(console.error);
