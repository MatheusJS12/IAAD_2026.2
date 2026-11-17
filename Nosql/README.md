# Minicurso NoSQL: Cloud Firestore (Torneio de Robótica)

## Requisitos
Node.js (LTS), Java (JDK 21) e Firebase CLI (`npm install -g firebase-tools`).

## Primeira vez
```bash
npm install
```

## Para rodar (use DOIS terminais dentro desta pasta)

**Terminal 1** (deixe aberto, é o banco):
```bash
npm run emulador
```
Painel visual: http://localhost:4000/firestore

**Terminal 2** (os comandos do vídeo, na ordem):
```bash
npm run carga             # carga inicial (7 equipes, 12 robôs, 15 resultados, 15 integrantes)
npm run create
npm run read
npm run update
npm run delete
npm run relacionamentos
```

Para recomeçar do zero: feche o emulador (Ctrl + C), ligue de novo e rode `npm run carga`.
Os dados do emulador somem quando ele é fechado.

## Modelagem
- `equipes/{id}` com a SUBCOLEÇÃO `integrantes/{id}` (tabela integrante do MySQL)
- `robos/{id}` com `equipe_id` (referência, equivale à FK)
- `resultados/{prova_classificacao}` com `robo_id` (referência) e `nome_robo` (cópia desnormalizada)
- O ID do resultado (ex.: `sumo-3kg_1`) reproduz a PK composta (nome_prova, classificacao) do MySQL.
