import sqlite3

conn = sqlite3.connect('data/dataset.sqlite')
cursor = conn.cursor()

cursor.execute("SELECT DISTINCT home_team_name FROM brazil_serie_a_matches1724")
times_casa = cursor.fetchall()

cursor.execute("SELECT DISTINCT away_team_name FROM brazil_serie_a_matches1724")
times_fora = cursor.fetchall()

# Combinar as listas de times (casa e fora) e remover duplicatas
todos_os_times = list(set(times_casa + times_fora))

print("Times na tabela:")
for time in todos_os_times:
    print(time[0])  # Acessando o nome do time na tupla

conn.close()
