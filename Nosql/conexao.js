// Conexão com o Firestore (emulador local).
// Se a variável FIRESTORE_EMULATOR_HOST não estiver definida, usamos o emulador padrão.
// Assim não é preciso configurar nada no terminal e nunca tocamos num banco real.
const admin = require("firebase-admin");

if (!process.env.FIRESTORE_EMULATOR_HOST) {
  process.env.FIRESTORE_EMULATOR_HOST = "localhost:8080";
}

admin.initializeApp({ projectId: "torneio-robotica" });
const db = admin.firestore();

const titulo = (t) => console.log(`\n========== ${t} ==========`);

// Converte Timestamp do Firestore para dd/mm/aaaa
const dataBR = (ts) =>
  ts.toDate().toISOString().slice(0, 10).split("-").reverse().join("/");

module.exports = { admin, db, titulo, dataBR };
