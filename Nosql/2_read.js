// READ: lendo dados do Firestore.
const { db, titulo, dataBR } = require("./conexao");

async function main() {
  titulo("READ 1 - por ID (equipe 1)");
  const eq = await db.collection("equipes").doc("1").get();
  console.log(eq.id, eq.data());

  titulo('READ 2 - filtro: robôs da categoria "Sumô"');
  const sumo = await db.collection("robos").where("categoria", "==", "Sumô").get();
  console.table(sumo.docs.map((d) => ({ id: d.id, nome_robo: d.data().nome_robo, categoria: d.data().categoria })));

  titulo("READ 3 - ordenação: 5 maiores pontuações do torneio");
  const top = await db.collection("resultados").orderBy("pontuacao", "desc").limit(5).get();
  console.table(
    top.docs.map((d) => {
      const r = d.data();
      return { prova: r.nome_prova, classificacao: r.classificacao, robo: r.nome_robo, pontuacao: r.pontuacao };
    })
  );

  titulo("READ 4 - intervalo de datas: robôs criados a partir de 01/01/2026");
  const novos = await db.collection("robos").where("data_criacao", ">=", new Date("2026-01-01")).orderBy("data_criacao").get();
  console.table(novos.docs.map((d) => ({ nome_robo: d.data().nome_robo, criado_em: dataBR(d.data().data_criacao) })));

  titulo('READ 5 - ranking de uma prova: "Mini Sumô"');
  // Obs.: em um projeto real (não emulador), filtro + ordenação em campos diferentes exige um índice composto.
  const rank = await db.collection("resultados").where("nome_prova", "==", "Mini Sumô").orderBy("classificacao").get();
  console.table(rank.docs.map((d) => ({ classificacao: d.data().classificacao, robo: d.data().nome_robo, pontuacao: d.data().pontuacao })));
}

main().catch(console.error);
