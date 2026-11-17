# Configuração da conexão com o MySQL.
# Troque a senha abaixo pela senha do seu MySQL (ou defina as variáveis
# de ambiente DB_HOST, DB_PORT, DB_USER e DB_PASSWORD).
import os

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "sua_senha_aqui"),
    "database": "torneio_robotica",
}
