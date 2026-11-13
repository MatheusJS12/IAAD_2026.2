# 🤖 Torneio de Robótica — Sistema de Gestão

![Python](https://img.shields.io/badge/Python-3.10+-06B6D4?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.50+-22D3EE?style=for-the-badge&logo=streamlit&logoColor=04222B)
![MySQL](https://img.shields.io/badge/MySQL-8.0+-0891B2?style=for-the-badge&logo=mysql&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-5.0+-155E75?style=for-the-badge&logo=plotly&logoColor=white)

Aplicação web desenvolvida em **Python**, **Streamlit**, **MySQL** e **Plotly** para o gerenciamento completo de um torneio de robótica. O sistema integra operações CRUD, consultas analíticas com *views*, *stored procedures*, *triggers*, integridade referencial e visualizações interativas em uma interface escura moderna com paleta monocromática em Ciano Robótica.

Projeto desenvolvido para a **2ª Verificação de Aprendizagem (2ª VA — 2026.2)** da disciplina **Introdução ao Armazenamento e Análise de Dados (IAAD)**, ministrada pela **Prof.ª Roberta Macêdo Marques Gouveia**, no curso de **Bacharelado em Sistemas de Informação** do **Departamento de Estatística e Informática (DEINFO)** da **Universidade Federal Rural de Pernambuco (UFRPE)**.

---

## ✨ Funcionalidades do Sistema

* **🏠 Início:** Painel inicial com contadores em tempo real de equipes, robôs, resultados e integrantes cadastrados no banco de dados.
* **👥 Equipes:** CRUD completo com busca dinâmica por nome, escola ou cidade, edição de ID com atualização em cascata e alerta prévio de registros dependentes antes da exclusão.
* **🤖 Robôs:** Gerenciamento de robôs inscritos com filtro múltiplo por categoria (`Sumô`, `Mini Sumô`, `Seguidor de Linha` e `Resgate`) e aviso de remoção em cascata de resultados vinculados.
* **🏆 Resultados:** Registro, edição e exclusão de classificações e pontuações (de `0` a `100`) com filtro por prova.
* **👤 Integrantes:** Cadastro de membros das equipes com atribuição de função (`Capitão`, `Programador`, `Mecânico`, `Eletrônica` e `Mentor`) e cálculo automático de idade via SQL (`TIMESTAMPDIFF`).
* **🔎 Consultas Não Triviais & Stored Procedure:**
  * Execução e inspeção do código SQL de 6 *views* (`vw_desempenho_equipe`, `vw_robos_sem_resultado`, `vw_idade_robos`, `vw_robos_por_mes`, `vw_estatisticas_categoria` e `vw_integrantes_equipe`).
  * Execução interativa da *stored procedure* `sp_ranking_prova` para geração do ranking por prova.
* **📊 Dashboard Interativo:**
  * Métricas principais (total de provas, média geral, maior pontuação e equipe líder).
  * 5 gráficos construídos com Plotly: pontuação total por equipe, distribuição de robôs por categoria, *boxplot* de pontuações por prova, comparativo de pontuação mínima/média/máxima por categoria e distribuição de equipes e robôs por cidade.
* **⚡ Integridade Referencial & Trigger:**
  * Demonstração prática de violação de chave estrangeira (`FK`), atualização/remoção em cascata e validação automática via *trigger* na inserção de resultados (pontuação entre `0` e `100`, classificação `>= 1` e bloqueio para robôs com data de criação futura).

---

## 🛠️ Tecnologias Utilizadas

| Tecnologia | Finalidade |
| :--- | :--- |
| **Python + Streamlit (`>=1.50`)** | Construção da interface web, navegação, formulários e gerenciamento de estado. |
| **MySQL + `mysql-connector-python` (`>=8.0`)** | Persistência relacional, *views*, *stored procedures*, *triggers* e tratamento de exceções SQL. |
| **Pandas (`>=2.0`)** | Manipulação tabular dos retornos de consultas e procedimentos armazenados. |
| **Plotly (`>=5.0`)** | Criação dos gráficos interativos harmonizados com o tema escuro da aplicação. |
| **CSS Customizado + `config.toml`** | Estilização em *Dark Mode* com paleta monocromática ciano (`#22D3EE` / `#06B6D4`) e tipografia `Inter` e `JetBrains Mono`. |

---

## 📁 Estrutura do Projeto

```text
app/
├── .streamlit/
│   └── config.toml          # Configuração nativa do tema escuro e cores primárias
├── app.py                   # Aplicação principal Streamlit, páginas, CSS e gráficos
├── config.py                # Parâmetros de conexão com o banco MySQL
├── db.py                    # Camada de acesso ao banco (CRUD, procedures e tratamento de erros)
├── requirements.txt         # Dependências Python do projeto
└── torneio_robotica.sql     # Script DDL/DML de criação do banco, tabelas, views, procedure e trigger
```

---

## 🚀 Como Executar o Projeto

### 1. Configure o Banco de Dados no MySQL
Certifique-se de que o servidor MySQL esteja ativo e execute o script `torneio_robotica.sql` (via MySQL Workbench ou linha de comando) para criar o banco `torneio_robotica` e seus objetos:

```bash
mysql -u root -p < torneio_robotica.sql
```

### 2. Defina as Credenciais de Acesso
Por segurança, a senha do banco não deve ser versionada no código. Defina as variáveis de ambiente no terminal antes de iniciar a aplicação (ou ajuste localmente o arquivo `config.py`):

```powershell
# Windows (PowerShell)
$env:DB_HOST="localhost"
$env:DB_PORT="3306"
$env:DB_USER="root"
$env:DB_PASSWORD="sua_senha_do_mysql"
```

```bash
# Linux / macOS
export DB_HOST="localhost"
export DB_PORT="3306"
export DB_USER="root"
export DB_PASSWORD="sua_senha_do_mysql"
```

### 3. Crie o Ambiente Virtual e Instale as Dependências
Na pasta `app/`, crie e ative um ambiente virtual e instale os pacotes listados em `requirements.txt`:

```bash
python -m venv venv

# Ativação no Windows:
venv\Scripts\activate

# Ativação no Linux / macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 4. Inicie a Aplicação
Execute o servidor do Streamlit:

```bash
streamlit run app.py
```

A aplicação ficará disponível automaticamente no navegador em `http://localhost:8501`.

---

## 👥 Equipe 4 — IAAD (2026.2)

* **Bruno Rodrigo Silva Lins**
* **Danielly Mendonça Nunes**
* **Guilherme Abraão Teixeira Bezerra**
* **Matheus Júlio da Silva**
* **Paulo Henrique da Fonseca Bezerra**
* **Thyago Murilo Ferreira dos Santos**
