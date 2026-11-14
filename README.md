# Torneio de Robótica · IAAD 2026.2

Aplicação local em Streamlit para gerenciar equipes, robôs, resultados e integrantes, com consultas, dashboard, integridade referencial e trigger do MySQL.

## Requisitos

- Python 3.10 ou superior
- MySQL 8 já configurado com o banco `torneio_robotica`
- Container MySQL publicado na porta local `3307` (porta interna `3306`)

## Iniciar o MySQL existente

Inicie o container existente, sem recriá-lo:

```bash
docker start torneio-mysql
```

Se o ambiente usa Podman, use `podman start torneio-mysql`. Para conferir o estado e a porta publicada:

```bash
docker ps --filter name=torneio-mysql
```

## Configurar e iniciar a aplicação

Na raiz do projeto:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r app/requirements.txt
```

Informe a senha existente do MySQL no terminal; ela não deve ser gravada no código ou em arquivos versionados:

```bash
export DB_HOST=127.0.0.1
export DB_PORT=3307
export DB_USER=root
read -s DB_PASSWORD
export DB_PASSWORD
```

Inicie a interface:

```bash
python -m streamlit run app/app.py
```

Abra o endereço local mostrado pelo Streamlit (normalmente `http://localhost:8501`). O tema pode ser alternado entre claro e escuro na barra lateral; o botão de recolher mantém os ícones de navegação visíveis.

## Banco de dados

`torneio_robotica.sql` contém `DROP DATABASE IF EXISTS torneio_robotica` e recria o schema e os dados de demonstração. **Não execute esse script sobre um banco com dados que deseja preservar.** Faça backup e confirme o alvo antes de qualquer carga. A aplicação não executa o SQL automaticamente.

O dashboard consulta os dados existentes nas tabelas e views. Se as tabelas estiverem vazias, os gráficos não recebem dados fictícios. Os cards dos integrantes do projeto usam os nomes fornecidos; somente os quatro perfis GitHub informados têm link.

## Navegação

- Início: indicadores e gráficos do torneio com seleção de itens para ver detalhes
- Equipes, Robôs, Resultados e Integrantes: operações CRUD
- Consultas: views e stored procedure
- Dashboard: análises existentes
- Integridade e Trigger: demonstrações de integridade referencial e validação

As credenciais são lidas das variáveis `DB_HOST`, `DB_PORT`, `DB_USER` e `DB_PASSWORD`. Padrões locais: `127.0.0.1:3307`, usuário `root` e senha vazia, que deve ser configurada no ambiente.
