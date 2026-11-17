# Funções de acesso ao banco usando mysql-connector-python.
from decimal import Decimal

import mysql.connector
import pandas as pd

from config import DB_CONFIG


def conectar():
    return mysql.connector.connect(**DB_CONFIG)


def _corrigir_texto(valor):
    """Corrige texto UTF-8 que foi lido como Latin-1 (ex.: ``SumÃ´``)."""
    if not isinstance(valor, str):
        return valor
    corrigido = valor
    for _ in range(3):
        if not any(marca in corrigido for marca in ("Ã", "Â", "â")):
            break
        novo = None
        for origem in ("latin1", "cp1252"):
            try:
                novo = corrigido.encode(origem).decode("utf-8")
                break
            except (UnicodeEncodeError, UnicodeDecodeError):
                continue
        if novo is None:
            break
        if novo == corrigido:
            break
        corrigido = novo
    return corrigido


def _converter(linha):
    # DECIMAL vem como Decimal; convertemos para float para os gráficos.
    # Também normalizamos mojibake sem alterar o conteúdo no banco.
    return {k: float(v) if isinstance(v, Decimal) else _corrigir_texto(v) for k, v in linha.items()}


def consultar(sql, params=None):
    """Executa um SELECT e devolve um DataFrame (Read)."""
    con = conectar()
    try:
        cur = con.cursor(dictionary=True)
        cur.execute(sql, params or ())
        linhas = [_converter(l) for l in cur.fetchall()]
        return pd.DataFrame(linhas, columns=cur.column_names)
    finally:
        con.close()


def executar(sql, params=None):
    """Executa INSERT, UPDATE ou DELETE e confirma (Create, Update, Delete)."""
    con = conectar()
    try:
        cur = con.cursor()
        cur.execute(sql, params or ())
        con.commit()
        return cur.rowcount
    except mysql.connector.Error:
        con.rollback()
        raise
    finally:
        con.close()


def chamar_procedure(nome, args):
    """Chama uma stored procedure e devolve o resultado como DataFrame."""
    con = conectar()
    try:
        cur = con.cursor()
        cur.callproc(nome, args)
        for res in cur.stored_results():
            colunas = [c[0] for c in res.description]
            linhas = [_converter(dict(zip(colunas, l))) for l in res.fetchall()]
            return pd.DataFrame(linhas, columns=colunas)
        return pd.DataFrame()
    finally:
        con.close()


def mensagem_erro(e):
    """Traduz os erros mais comuns do MySQL para mensagens claras."""
    codigos = {
        1452: "Violação de integridade referencial (FK): o registro relacionado não existe.",
        1451: "Não é possível remover: existem registros que dependem deste.",
        1062: "Registro duplicado: já existe um registro com essa chave.",
        1644: "Operação bloqueada pela trigger.",
        1048: "Campo obrigatório não preenchido.",
        1406: "Texto maior do que o permitido para o campo.",
    }
    base = codigos.get(e.errno, "Erro no banco de dados.")
    return f"{base}\n\nMySQL {e.errno}: {e.msg}"
