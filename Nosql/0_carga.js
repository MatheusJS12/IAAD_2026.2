// CARGA INICIAL: grava no Firestore os mesmos dados do script MySQL.
const { db, titulo } = require("./conexao");
const { equipes, robos, resultados, integrantes, idResultado } = require("./dados");

async function main() {
  titulo("CARGA INICIAL");
  const batch = db.batch(); // várias escritas em uma só operação (como uma transação)

  for (const { id, ...campos } of equipes) {
    batch.set(db.collection("equipes").doc(id), campos);
  }

  for (const { id, equipe_id, ...campos } of integrantes) {
    // subcoleção: equipes/{equipe_id}/integrantes/{id}
    batch.set(db.collection("equipes").doc(equipe_id).collection("integrantes").doc(id), campos);
  }

  for (const { id, ...campos } of robos) {
    batch.set(db.collection("robos").doc(id), campos); // equipe_id é a referência (equivale à FK)
  }

  for (const r of resultados) {
    const robo = robos.find((x) => x.id === r.robo_id);
    batch.set(db.collection("resultados").doc(idResultado(r)), {
      ...r,
      nome_robo: robo.nome_robo, // cópia (desnormalização) para ler o ranking sem buscar o robô
    });
  }

  await batch.commit();
  console.log(`equipes: ${equipes.length} | integrantes: ${integrantes.length} | robos: ${robos.length} | resultados: ${resultados.length}`);
  console.log("Carga concluída. Abra http://localhost:4000/firestore para ver os dados.");
}

main().catch(console.error);
