import sqlite3

# Conecta ao banco de dados SQLite
conn = sqlite3.connect('./data/dataset.sqlite')
cursor = conn.cursor()

# Define as colunas que você quer consultar
colunas = [
    "home_goals_scored_rolling_avg",
    "home_goals_conceded_rolling_avg",
    "away_goals_scored_rolling_avg",
    "away_goals_conceded_rolling_avg"
]

# Loop pelas colunas e imprime os últimos 10 valores
for coluna in colunas:
    cursor.execute(f"SELECT {coluna} FROM premier_matches1724 ORDER BY date DESC LIMIT 100")
    resultados = cursor.fetchall()

    print(f"Últimos 10 valores de '{coluna}':")
    for resultado in resultados:
        print(resultado[0])  # Imprime o valor da coluna
    print("-" * 30)

# Fecha a conexão com o banco de dados
conn.close()
