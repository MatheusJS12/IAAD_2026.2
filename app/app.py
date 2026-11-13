# Sistema web do Torneio de Robótica (IAAD 2026.2 - 2ª VA)
# Execução: streamlit run app.py
import datetime as dt

import mysql.connector
import plotly.express as px
import streamlit as st

from db import chamar_procedure, consultar, executar, mensagem_erro

st.set_page_config(page_title="Torneio de Robótica", page_icon="🤖", layout="wide")

CATEGORIAS = ["Sumô", "Mini Sumô", "Seguidor de Linha", "Resgate"]
FUNCOES = ["Capitão", "Programador", "Mecânico", "Eletrônica", "Mentor"]
DATA_MIN, DATA_MAX = dt.date(1950, 1, 1), dt.date(2035, 12, 31)


# ---------------------------------------------------------------------
# Utilitários
# ---------------------------------------------------------------------

def sucesso(msg):
    """Guarda a mensagem e recarrega a página para atualizar as listas."""
    st.session_state["flash"] = msg
    st.rerun()


def rodar(sql, params, msg_ok):
    """Executa um comando e mostra sucesso ou o erro do MySQL."""
    try:
        executar(sql, params)
        sucesso(msg_ok)
    except mysql.connector.Error as e:
        st.error(mensagem_erro(e))


def opcoes_equipes():
    df = consultar("SELECT id_equipe, nome_equipe FROM equipe ORDER BY nome_equipe")
    return {f"{r.nome_equipe} (id {r.id_equipe})": r.id_equipe for r in df.itertuples()}


def opcoes_robos():
    df = consultar("""SELECT ro.id_robo, ro.nome_robo, e.nome_equipe
                        FROM robo ro JOIN equipe e ON e.id_equipe = ro.id_equipe
                       ORDER BY ro.nome_robo""")
    return {f"{r.nome_robo} - {r.nome_equipe} (id {r.id_robo})": r.id_robo for r in df.itertuples()}


def chave_de(dic, valor):
    """Devolve o índice da opção cujo valor é 'valor' (para pré-selecionar)."""
    valores = list(dic.values())
    return valores.index(valor) if valor in valores else 0


# ---------------------------------------------------------------------
# Páginas
# ---------------------------------------------------------------------

def pagina_inicio():
    st.title("🤖 Torneio de Robótica")
    st.write("Sistema de gerenciamento do torneio com MySQL, Streamlit e Plotly.")
    c = consultar("""SELECT (SELECT COUNT(*) FROM equipe)     AS equipes,
                            (SELECT COUNT(*) FROM robo)       AS robos,
                            (SELECT COUNT(*) FROM resultado)  AS resultados,
                            (SELECT COUNT(*) FROM integrante) AS integrantes""").iloc[0]
    col = st.columns(4)
    col[0].metric("Equipes", int(c.equipes))
    col[1].metric("Robôs", int(c.robos))
    col[2].metric("Resultados", int(c.resultados))
    col[3].metric("Integrantes", int(c.integrantes))
    st.markdown("""
**Menu lateral**
- **Equipes, Robôs, Resultados e Integrantes:** CRUD completo de cada tabela
- **Consultas:** consultas não triviais (JOIN, GROUP BY, agregação, datas) e a stored procedure
- **Dashboard:** gráficos interativos
- **Integridade e Trigger:** demonstração das FKs, da cascata e da trigger
""")


def pagina_equipes():
    st.header("Equipes")
    listar, criar, editar, excluir = st.tabs(["Listar", "Cadastrar", "Editar", "Excluir"])

    with listar:
        busca = st.text_input("Buscar por nome, escola ou cidade")
        like = f"%{busca}%"
        df = consultar("""SELECT * FROM equipe
                           WHERE nome_equipe LIKE %s OR escola LIKE %s OR cidade LIKE %s
                           ORDER BY id_equipe""", (like, like, like))
        st.dataframe(df, hide_index=True, width="stretch")

    with criar:
        with st.form("form_criar_equipe", clear_on_submit=True):
            nome = st.text_input("Nome da equipe")
            escola = st.text_input("Escola")
            cidade = st.text_input("Cidade")
            if st.form_submit_button("Cadastrar"):
                if not (nome and escola and cidade):
                    st.warning("Preencha todos os campos.")
                else:
                    rodar("INSERT INTO equipe (nome_equipe, escola, cidade) VALUES (%s, %s, %s)",
                          (nome, escola, cidade), f"Equipe '{nome}' cadastrada.")

    with editar:
        opcoes = opcoes_equipes()
        if not opcoes:
            st.info("Nenhuma equipe cadastrada.")
        else:
            id_eq = opcoes[st.selectbox("Equipe", opcoes, key="sel_edit_eq")]
            eq = consultar("SELECT * FROM equipe WHERE id_equipe = %s", (id_eq,)).iloc[0]
            with st.form("form_editar_equipe"):
                novo_id = st.number_input("ID da equipe", value=int(eq.id_equipe), step=1,
                                          key=f"eq_id_{id_eq}",
                                          help="Alterar o ID atualiza em cascata os robôs e integrantes.")
                nome = st.text_input("Nome da equipe", eq.nome_equipe, key=f"eq_nome_{id_eq}")
                escola = st.text_input("Escola", eq.escola, key=f"eq_esc_{id_eq}")
                cidade = st.text_input("Cidade", eq.cidade, key=f"eq_cid_{id_eq}")
                if st.form_submit_button("Salvar alterações"):
                    rodar("""UPDATE equipe SET id_equipe = %s, nome_equipe = %s, escola = %s, cidade = %s
                              WHERE id_equipe = %s""",
                          (int(novo_id), nome, escola, cidade, id_eq), "Equipe atualizada.")

    with excluir:
        opcoes = opcoes_equipes()
        if not opcoes:
            st.info("Nenhuma equipe cadastrada.")
        else:
            rotulo = st.selectbox("Equipe", opcoes, key="sel_del_eq")
            id_eq = opcoes[rotulo]
            dep = consultar("""SELECT (SELECT COUNT(*) FROM robo WHERE id_equipe = %s) AS robos,
                                      (SELECT COUNT(*) FROM resultado r JOIN robo ro ON ro.id_robo = r.id_robo
                                        WHERE ro.id_equipe = %s) AS resultados,
                                      (SELECT COUNT(*) FROM integrante WHERE id_equipe = %s) AS integrantes""",
                            (id_eq, id_eq, id_eq)).iloc[0]
            st.warning(f"Remoção em cascata: também serão apagados {int(dep.robos)} robô(s), "
                       f"{int(dep.resultados)} resultado(s) e {int(dep.integrantes)} integrante(s).")
            if st.checkbox("Confirmo a exclusão", key=f"conf_del_eq_{id_eq}"):
                if st.button("Excluir equipe", type="primary"):
                    rodar("DELETE FROM equipe WHERE id_equipe = %s", (id_eq,), f"Equipe '{rotulo}' excluída.")


def pagina_robos():
    st.header("Robôs")
    listar, criar, editar, excluir = st.tabs(["Listar", "Cadastrar", "Editar", "Excluir"])

    with listar:
        cats = st.multiselect("Filtrar por categoria", CATEGORIAS)
        sql = """SELECT ro.id_robo, ro.nome_robo, ro.categoria, ro.data_criacao, e.nome_equipe
                   FROM robo ro JOIN equipe e ON e.id_equipe = ro.id_equipe"""
        if cats:
            sql += " WHERE ro.categoria IN (" + ",".join(["%s"] * len(cats)) + ")"
        df = consultar(sql + " ORDER BY ro.id_robo", tuple(cats))
        st.dataframe(df, hide_index=True, width="stretch",
                     column_config={"data_criacao": st.column_config.DateColumn("data_criacao", format="DD/MM/YYYY")})

    with criar:
        equipes = opcoes_equipes()
        with st.form("form_criar_robo", clear_on_submit=True):
            nome = st.text_input("Nome do robô")
            categoria = st.selectbox("Categoria", CATEGORIAS)
            data = st.date_input("Data de criação", dt.date.today(), DATA_MIN, DATA_MAX, format="DD/MM/YYYY")
            equipe = st.selectbox("Equipe", equipes)
            if st.form_submit_button("Cadastrar"):
                if not nome or not equipe:
                    st.warning("Informe o nome e a equipe.")
                else:
                    rodar("""INSERT INTO robo (nome_robo, categoria, data_criacao, id_equipe)
                             VALUES (%s, %s, %s, %s)""",
                          (nome, categoria, data, equipes[equipe]), f"Robô '{nome}' cadastrado.")

    with editar:
        robos, equipes = opcoes_robos(), opcoes_equipes()
        if not robos:
            st.info("Nenhum robô cadastrado.")
        else:
            id_r = robos[st.selectbox("Robô", robos, key="sel_edit_robo")]
            r = consultar("SELECT * FROM robo WHERE id_robo = %s", (id_r,)).iloc[0]
            with st.form("form_editar_robo"):
                nome = st.text_input("Nome do robô", r.nome_robo, key=f"r_nome_{id_r}")
                cat_idx = CATEGORIAS.index(r.categoria) if r.categoria in CATEGORIAS else 0
                categoria = st.selectbox("Categoria", CATEGORIAS, cat_idx, key=f"r_cat_{id_r}")
                data = st.date_input("Data de criação", r.data_criacao, DATA_MIN, DATA_MAX,
                                     format="DD/MM/YYYY", key=f"r_data_{id_r}")
                equipe = st.selectbox("Equipe", equipes, chave_de(equipes, r.id_equipe), key=f"r_eq_{id_r}")
                if st.form_submit_button("Salvar alterações"):
                    rodar("""UPDATE robo SET nome_robo = %s, categoria = %s, data_criacao = %s, id_equipe = %s
                              WHERE id_robo = %s""",
                          (nome, categoria, data, equipes[equipe], id_r), "Robô atualizado.")

    with excluir:
        robos = opcoes_robos()
        if not robos:
            st.info("Nenhum robô cadastrado.")
        else:
            rotulo = st.selectbox("Robô", robos, key="sel_del_robo")
            id_r = robos[rotulo]
            n = consultar("SELECT COUNT(*) AS n FROM resultado WHERE id_robo = %s", (id_r,)).iloc[0].n
            st.warning(f"Remoção em cascata: {int(n)} resultado(s) deste robô também serão apagados.")
            if st.checkbox("Confirmo a exclusão", key=f"conf_del_r_{id_r}"):
                if st.button("Excluir robô", type="primary"):
                    rodar("DELETE FROM robo WHERE id_robo = %s", (id_r,), f"Robô '{rotulo}' excluído.")


def pagina_resultados():
    st.header("Resultados")
    listar, criar, editar, excluir = st.tabs(["Listar", "Cadastrar", "Editar", "Excluir"])
    provas = consultar("SELECT DISTINCT nome_prova FROM resultado ORDER BY nome_prova").nome_prova.tolist()

    with listar:
        prova = st.selectbox("Filtrar por prova", ["Todas"] + provas)
        sql = """SELECT r.nome_prova, r.classificacao, r.pontuacao, ro.nome_robo, e.nome_equipe
                   FROM resultado r
                   JOIN robo ro  ON ro.id_robo  = r.id_robo
                   JOIN equipe e ON e.id_equipe = ro.id_equipe"""
        params = ()
        if prova != "Todas":
            sql += " WHERE r.nome_prova = %s"
            params = (prova,)
        df = consultar(sql + " ORDER BY r.nome_prova, r.classificacao", params)
        st.dataframe(df, hide_index=True, width="stretch")

    with criar:
        robos = opcoes_robos()
        st.caption("Provas existentes: " + ", ".join(provas))
        with st.form("form_criar_resultado", clear_on_submit=True):
            nome_prova = st.text_input("Nome da prova")
            classificacao = st.number_input("Classificação", value=1, step=1)
            pontuacao = st.number_input("Pontuação (0 a 100)", value=0.0, step=0.5, format="%.2f")
            robo = st.selectbox("Robô", robos)
            if st.form_submit_button("Cadastrar"):
                if not nome_prova or not robo:
                    st.warning("Informe a prova e o robô.")
                else:
                    rodar("""INSERT INTO resultado (nome_prova, classificacao, pontuacao, id_robo)
                             VALUES (%s, %s, %s, %s)""",
                          (nome_prova, int(classificacao), pontuacao, robos[robo]), "Resultado cadastrado.")

    df_res = consultar("""SELECT r.*, ro.nome_robo FROM resultado r
                          JOIN robo ro ON ro.id_robo = r.id_robo
                          ORDER BY r.nome_prova, r.classificacao""")
    chaves = {f"{r.nome_prova} - {r.classificacao}º lugar ({r.nome_robo})": (r.nome_prova, r.classificacao)
              for r in df_res.itertuples()}

    with editar:
        if not chaves:
            st.info("Nenhum resultado cadastrado.")
        else:
            robos = opcoes_robos()
            prova, clas = chaves[st.selectbox("Resultado", chaves, key="sel_edit_res")]
            r = df_res[(df_res.nome_prova == prova) & (df_res.classificacao == clas)].iloc[0]
            k = f"{prova}_{clas}"
            with st.form("form_editar_resultado"):
                nova_prova = st.text_input("Nome da prova", r.nome_prova, key=f"res_p_{k}")
                nova_clas = st.number_input("Classificação", value=int(r.classificacao), step=1, key=f"res_c_{k}")
                pont = st.number_input("Pontuação (0 a 100)", value=float(r.pontuacao), step=0.5,
                                       format="%.2f", key=f"res_pt_{k}")
                robo = st.selectbox("Robô", robos, chave_de(robos, r.id_robo), key=f"res_r_{k}")
                if st.form_submit_button("Salvar alterações"):
                    rodar("""UPDATE resultado SET nome_prova = %s, classificacao = %s, pontuacao = %s, id_robo = %s
                              WHERE nome_prova = %s AND classificacao = %s""",
                          (nova_prova, int(nova_clas), pont, robos[robo], prova, int(clas)),
                          "Resultado atualizado.")

    with excluir:
        if not chaves:
            st.info("Nenhum resultado cadastrado.")
        else:
            rotulo = st.selectbox("Resultado", chaves, key="sel_del_res")
            prova, clas = chaves[rotulo]
            if st.button("Excluir resultado", type="primary"):
                rodar("DELETE FROM resultado WHERE nome_prova = %s AND classificacao = %s",
                      (prova, int(clas)), f"Resultado '{rotulo}' excluído.")


def pagina_integrantes():
    st.header("Integrantes")
    listar, criar, editar, excluir = st.tabs(["Listar", "Cadastrar", "Editar", "Excluir"])

    with listar:
        df = consultar("""SELECT i.id_integrante, i.nome_integrante, i.funcao, i.data_nascimento,
                                 TIMESTAMPDIFF(YEAR, i.data_nascimento, CURDATE()) AS idade,
                                 i.email, e.nome_equipe
                            FROM integrante i JOIN equipe e ON e.id_equipe = i.id_equipe
                           ORDER BY e.nome_equipe, i.nome_integrante""")
        st.dataframe(df, hide_index=True, width="stretch",
                     column_config={"data_nascimento": st.column_config.DateColumn("data_nascimento", format="DD/MM/YYYY")})

    with criar:
        equipes = opcoes_equipes()
        with st.form("form_criar_integrante", clear_on_submit=True):
            nome = st.text_input("Nome")
            funcao = st.selectbox("Função", FUNCOES)
            nasc = st.date_input("Data de nascimento", dt.date(2008, 1, 1), DATA_MIN, DATA_MAX, format="DD/MM/YYYY")
            email = st.text_input("E-mail (opcional)")
            equipe = st.selectbox("Equipe", equipes)
            if st.form_submit_button("Cadastrar"):
                if not nome or not equipe:
                    st.warning("Informe o nome e a equipe.")
                else:
                    rodar("""INSERT INTO integrante (nome_integrante, funcao, data_nascimento, email, id_equipe)
                             VALUES (%s, %s, %s, %s, %s)""",
                          (nome, funcao, nasc, email or None, equipes[equipe]), f"Integrante '{nome}' cadastrado.")

    df_int = consultar("SELECT * FROM integrante ORDER BY nome_integrante")
    pessoas = {f"{r.nome_integrante} (id {r.id_integrante})": r.id_integrante for r in df_int.itertuples()}

    with editar:
        if not pessoas:
            st.info("Nenhum integrante cadastrado.")
        else:
            equipes = opcoes_equipes()
            id_i = pessoas[st.selectbox("Integrante", pessoas, key="sel_edit_int")]
            r = df_int[df_int.id_integrante == id_i].iloc[0]
            with st.form("form_editar_integrante"):
                nome = st.text_input("Nome", r.nome_integrante, key=f"i_nome_{id_i}")
                f_idx = FUNCOES.index(r.funcao) if r.funcao in FUNCOES else 0
                funcao = st.selectbox("Função", FUNCOES, f_idx, key=f"i_func_{id_i}")
                nasc = st.date_input("Data de nascimento", r.data_nascimento, DATA_MIN, DATA_MAX,
                                     format="DD/MM/YYYY", key=f"i_nasc_{id_i}")
                email = st.text_input("E-mail", r.email or "", key=f"i_mail_{id_i}")
                equipe = st.selectbox("Equipe", equipes, chave_de(equipes, r.id_equipe), key=f"i_eq_{id_i}")
                if st.form_submit_button("Salvar alterações"):
                    rodar("""UPDATE integrante SET nome_integrante = %s, funcao = %s, data_nascimento = %s,
                                    email = %s, id_equipe = %s
                              WHERE id_integrante = %s""",
                          (nome, funcao, nasc, email or None, equipes[equipe], id_i), "Integrante atualizado.")

    with excluir:
        if not pessoas:
            st.info("Nenhum integrante cadastrado.")
        else:
            rotulo = st.selectbox("Integrante", pessoas, key="sel_del_int")
            if st.button("Excluir integrante", type="primary"):
                rodar("DELETE FROM integrante WHERE id_integrante = %s", (pessoas[rotulo],),
                      f"Integrante '{rotulo}' excluído.")


CONSULTAS = {
    "Desempenho por equipe (JOIN + GROUP BY + SUM/AVG/MAX)":
        "SELECT * FROM vw_desempenho_equipe ORDER BY pontuacao_total DESC",
    "Robôs sem resultado (LEFT JOIN exclusiva)":
        "SELECT * FROM vw_robos_sem_resultado",
    "Idade dos robôs (manipulação de datas)":
        "SELECT * FROM vw_idade_robos ORDER BY idade_dias DESC",
    "Robôs criados por mês (datas + COUNT)":
        "SELECT * FROM vw_robos_por_mes ORDER BY mes",
    "Estatísticas por categoria (MIN/MAX/AVG)":
        "SELECT * FROM vw_estatisticas_categoria",
    "Integrantes e idade média por equipe":
        "SELECT * FROM vw_integrantes_equipe ORDER BY nome_equipe",
}


def pagina_consultas():
    st.header("Consultas não triviais")
    escolha = st.selectbox("Consulta", CONSULTAS)
    sql = CONSULTAS[escolha]
    view = sql.split("FROM ")[1].split()[0]
    definicao = consultar("""SELECT VIEW_DEFINITION FROM information_schema.VIEWS
                              WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s""", (view,))
    st.dataframe(consultar(sql), hide_index=True, width="stretch")
    if not definicao.empty:
        with st.expander("Ver o SQL da view"):
            st.code(definicao.iloc[0, 0], language="sql")

    st.divider()
    st.subheader("Stored procedure: ranking de uma prova")
    st.code("CALL sp_ranking_prova('<nome da prova>');", language="sql")
    provas = consultar("SELECT DISTINCT nome_prova FROM resultado ORDER BY nome_prova").nome_prova.tolist()
    if provas:
        prova = st.selectbox("Prova", provas)
        st.dataframe(chamar_procedure("sp_ranking_prova", (prova,)), hide_index=True, width="stretch")


def pagina_dashboard():
    st.header("Dashboard")
    desemp = consultar("SELECT * FROM vw_desempenho_equipe")
    res = consultar("""SELECT r.nome_prova, r.pontuacao, ro.categoria, ro.nome_robo, e.nome_equipe
                         FROM resultado r
                         JOIN robo ro  ON ro.id_robo  = r.id_robo
                         JOIN equipe e ON e.id_equipe = ro.id_equipe""")

    col = st.columns(4)
    col[0].metric("Provas", res.nome_prova.nunique())
    col[1].metric("Média geral", f"{res.pontuacao.mean():.2f}" if not res.empty else "-")
    col[2].metric("Maior pontuação", f"{res.pontuacao.max():.2f}" if not res.empty else "-")
    lider = desemp.sort_values("pontuacao_total", ascending=False).iloc[0] if not desemp.empty else None
    col[3].metric("Equipe líder", lider.nome_equipe if lider is not None else "-")

    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(desemp.sort_values("pontuacao_total"), x="pontuacao_total", y="nome_equipe",
                     orientation="h", title="Pontuação total por equipe",
                     labels={"pontuacao_total": "Pontos", "nome_equipe": ""})
        st.plotly_chart(fig, width="stretch")
    with c2:
        cat = consultar("SELECT categoria, COUNT(*) AS qtd FROM robo GROUP BY categoria")
        fig = px.pie(cat, names="categoria", values="qtd", hole=0.45, title="Robôs por categoria")
        st.plotly_chart(fig, width="stretch")

    c3, c4 = st.columns(2)
    with c3:
        fig = px.box(res, x="nome_prova", y="pontuacao", points="all", hover_data=["nome_robo"],
                     title="Distribuição das pontuações por prova",
                     labels={"nome_prova": "", "pontuacao": "Pontuação"})
        st.plotly_chart(fig, width="stretch")
    with c4:
        est = consultar("SELECT * FROM vw_estatisticas_categoria ORDER BY media_pontuacao DESC")
        fig = px.bar(est, x="categoria", y=["menor_pontuacao", "media_pontuacao", "maior_pontuacao"],
                     barmode="group", title="Pontuação por categoria (mínima, média e máxima)",
                     labels={"categoria": "", "value": "Pontuação", "variable": ""})
        st.plotly_chart(fig, width="stretch")

    cid = consultar("""SELECT e.cidade, COUNT(DISTINCT e.id_equipe) AS equipes, COUNT(ro.id_robo) AS robos
                         FROM equipe e LEFT JOIN robo ro ON ro.id_equipe = e.id_equipe
                        GROUP BY e.cidade ORDER BY robos DESC""")
    fig = px.bar(cid, x="cidade", y=["equipes", "robos"], barmode="group", title="Equipes e robôs por cidade",
                 labels={"cidade": "", "value": "Quantidade", "variable": ""})
    st.plotly_chart(fig, width="stretch")


def pagina_integridade():
    st.header("Integridade referencial e trigger")

    st.subheader("1. Violação de chave estrangeira")
    st.write("Tenta cadastrar um robô ligado a uma equipe que não existe.")
    id_falso = st.number_input("ID da equipe", value=999, step=1)
    if st.button("Inserir robô com esse ID de equipe"):
        rodar("INSERT INTO robo (nome_robo, categoria, data_criacao, id_equipe) VALUES (%s, %s, %s, %s)",
              ("Robô Teste FK", "Sumô", dt.date.today(), int(id_falso)),
              f"Robô inserido (a equipe {int(id_falso)} existe).")

    st.subheader("2. Atualização e remoção em cascata")
    st.write("Use as abas **Editar** (alterando o ID) e **Excluir** da página **Equipes**. "
             "O sistema mostra antes quantos registros dependentes serão afetados.")

    st.subheader("3. Trigger de validação de resultados")
    trig = consultar("""SELECT TRIGGER_NAME, EVENT_MANIPULATION AS evento, ACTION_TIMING AS momento,
                               EVENT_OBJECT_TABLE AS tabela
                          FROM information_schema.TRIGGERS WHERE TRIGGER_SCHEMA = DATABASE()""")
    st.dataframe(trig, hide_index=True, width="stretch")
    st.write("Regras: pontuação entre 0 e 100, classificação 1 ou maior "
             "e robô com data de criação futura não pode ter resultado.")
    robos = opcoes_robos()
    with st.form("form_trigger"):
        prova = st.text_input("Prova", "Teste Trigger")
        clas = st.number_input("Classificação", value=1, step=1)
        pont = st.number_input("Pontuação", value=150.0, step=0.5, format="%.2f")
        robo = st.selectbox("Robô", robos)
        if st.form_submit_button("Inserir resultado"):
            rodar("INSERT INTO resultado (nome_prova, classificacao, pontuacao, id_robo) VALUES (%s, %s, %s, %s)",
                  (prova, int(clas), pont, robos[robo]), "Resultado aceito pela trigger.")


# ---------------------------------------------------------------------
# Menu
# ---------------------------------------------------------------------

PAGINAS = {
    "Início": pagina_inicio,
    "Equipes": pagina_equipes,
    "Robôs": pagina_robos,
    "Resultados": pagina_resultados,
    "Integrantes": pagina_integrantes,
    "Consultas": pagina_consultas,
    "Dashboard": pagina_dashboard,
    "Integridade e Trigger": pagina_integridade,
}

st.sidebar.title("Menu")
escolha = st.sidebar.radio("Página", list(PAGINAS), label_visibility="collapsed")

if "flash" in st.session_state:
    st.success(st.session_state.pop("flash"))

try:
    PAGINAS[escolha]()
except mysql.connector.Error as e:
    st.error("Não foi possível acessar o banco. Verifique se o MySQL está rodando, "
             "se o script torneio_robotica.sql foi executado e se a senha em config.py está correta.")
    st.code(str(e))
