// CONSULTAS COM RELACIONAMENTO (o que no MySQL seria JOIN / GROUP BY / VIEW).
const { db, titulo } = require("./conexao");

// Busca um documento por ID e devolve os dados (ou null se não existir)
const dados = async (colecao, id) => {
  const d = await db.collection(colecao).doc(id).get();
  return d.exists ? d.data() : null;
};

async function main() {
  // ---------------------------------------------------------------
  titulo("A) Robôs de uma equipe (JOIN robo + equipe = 2 consultas)");
  const eqSnap = await db.collection("equipes").where("nome_equipe", "==", "RoboRecife").get();
  const equipe = eqSnap.docs[0];
  const robos = await db.collection("robos").where("equipe_id", "==", equipe.id).get();
  console.table(
    robos.docs.map((d) => ({ robo: d.data().nome_robo, categoria: d.data().categoria, equipe: equipe.data().nome_equipe }))
  );

  // ---------------------------------------------------------------
  titulo('B) Ranking de uma prova com robô, equipe e escola (equivale à sp_ranking_prova("Sumô 3kg"))');
  const res = await db.collection("resultados").where("nome_prova", "==", "Sumô 3kg").orderBy("classificacao").get();
  const ranking = await Promise.all(
    res.docs.map(async (d) => {
      const r = d.data();
      const robo = await dados("robos", r.robo_id);                      // resultado -> robô
      const eq = robo ? await dados("equipes", robo.equipe_id) : null;   // robô -> equipe
      return {
        classificacao: r.classificacao,
        robo: robo?.nome_robo ?? r.nome_robo,
        equipe: eq?.nome_equipe ?? "(equipe removida)",
        escola: eq?.escola ?? "-",
        pontuacao: r.pontuacao,
      };
    })
  );
  console.table(ranking);

  // ---------------------------------------------------------------
  titulo("C) Integrantes de uma equipe (SUBCOLEÇÃO: sem JOIN, os dados já estão dentro da equipe)");
  const integ = await db.collection("equipes").doc("1").collection("integrantes").get();
  console.table(integ.docs.map((d) => ({ nome: d.data().nome_integrante, funcao: d.data().funcao })));

  // ---------------------------------------------------------------
  titulo('D) Todos os "Programador" de todas as equipes (collection group query)');
  // Em projeto real, este tipo de consulta exige criar um índice de "collection group".
  const progs = await db.collectionGroup("integrantes").where("funcao", "==", "Programador").get();
  const linhasProg = await Promise.all(
    progs.docs.map(async (d) => {
      const eq = await d.ref.parent.parent.get(); // sobe um nível: o documento da equipe dona
      return { nome: d.data().nome_integrante, funcao: d.data().funcao, equipe: eq.exists ? eq.data().nome_equipe : "(equipe removida)" };
    })
  );
  console.table(linhasProg);

  // ---------------------------------------------------------------
  titulo("E) Desempenho por equipe (equivale à view vw_desempenho_equipe: JOIN + GROUP BY)");
  const [eqs, rbs, rss] = await Promise.all([
    db.collection("equipes").get(),
    db.collection("robos").get(),
    db.collection("resultados").get(),
  ]);
  const equipeDoRobo = {};
  rbs.forEach((d) => (equipeDoRobo[d.id] = d.data().equipe_id));
  const acc = {};
  eqs.forEach((d) => (acc[d.id] = { equipe: d.data().nome_equipe, participacoes: 0, total: 0, melhor: 0, primeiros: 0 }));
  rss.forEach((d) => {
    const r = d.data();
    const e = acc[equipeDoRobo[r.robo_id]];
    if (!e) return;
    e.participacoes++;
    e.total += r.pontuacao;
    e.melhor = Math.max(e.melhor, r.pontuacao);
    if (r.classificacao === 1) e.primeiros++;
  });
  console.table(
    Object.values(acc)
      .map((e) => ({
        equipe: e.equipe,
        participacoes: e.participacoes,
        total: +e.total.toFixed(2),
        media: e.participacoes ? +(e.total / e.participacoes).toFixed(2) : null,
        melhor: e.melhor,
        primeiros_lugares: e.primeiros,
      }))
      .sort((a, b) => b.total - a.total)
  );

  // ---------------------------------------------------------------
  titulo("F) Robôs sem nenhum resultado (equivale a LEFT JOIN ... WHERE r.id_robo IS NULL)");
  const comResultado = new Set(rss.docs.map((d) => d.data().robo_id));
  console.table(
    rbs.docs
      .filter((d) => !comResultado.has(d.id))
      .map((d) => ({ id: d.id, robo: d.data().nome_robo, categoria: d.data().categoria }))
  );
}

main().catch(console.error);
