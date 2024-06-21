import sqlite3
import pandas as pd
import os
import sys
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkinter import font

from src.utils.Kelly_Criterion import calculate_kelly_criterion
from src.utils.Expected_Value import expected_value
from src.utils.dicts import premier_league_teams, brasileirao_a_teams, brasileirao_b_teams, features

def resource_path(relative_path):
    """Get the absolute path to the resource, works for PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def center_window(window):
    """Centraliza a janela na tela."""
    window.update_idletasks()  # Atualiza o layout da janela
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    window_width = window.winfo_width()
    window_height = window.winfo_height()
    x = int((screen_width / 2) - (window_width / 2))
    y = int((screen_height / 2) - (window_height / 2))
    window.geometry(f"+{x}+{y}")

    
# Função para preparar os dados
def prepare_data(data, liga):
    if liga == "premier":
        random_state = 206
    elif liga == "brasileirao_a":
        random_state = 348
    elif liga == "brasileirao_b":
        random_state = 458
    else:
        raise ValueError("Liga inválida.")
    
    X = data[features]
    y = data["home_team_win"]
    return train_test_split(X, y, test_size=0.2, random_state=random_state)

# Função para treinar o modelo
def train_model(X_train, y_train, liga):
    if liga == "premier":
        random_state = 206
        min_samples_leaf = 4
        min_samples_split = 15
        n_estimators = 400
    elif liga == "brasileirao_a":
        random_state = 348
        min_samples_leaf = 2
        min_samples_split = 10
        n_estimators = 600
    elif liga == "brasileirao_b":
        random_state = 458
        min_samples_leaf = 2
        min_samples_split = 5
        n_estimators = 200
    else:
        raise ValueError("Liga inválida.")

    model = RandomForestClassifier(random_state=random_state, 
                                   min_samples_leaf=min_samples_leaf, 
                                   min_samples_split=min_samples_split, 
                                   n_estimators=n_estimators)
    
    model.fit(X_train, y_train)
    return model

# Função para prever a partida
def predict_match(model, match_data):
    prediction = model.predict_proba(match_data)[0]
    return prediction  # Probabilidade de vitória do time da casa

def show_prediction(home_team, away_team, probabilities, odds_home, odds_draw, odds_away):
    draw_prob, home_win_prob, away_win_prob = probabilities

    # Crie uma nova janela (Toplevel)
    prediction_window = tk.Toplevel()
    prediction_window.title("Previsão da Partida")

    # Crie um frame para o conteúdo
    content_frame = tk.Frame(prediction_window, )
    content_frame.pack(padx=20, pady=20)
    
    title_label = tk.Label(
        content_frame, 
        text=f"Partida: {home_team} vs {away_team}", 
        font=("Arial", 14, "bold"),  # Fonte maior e em negrito
        anchor="center"  # Centraliza o texto
    )
    title_label.pack(pady=10)
    
    # Crie o label com o texto da previsão
    result_label = tk.Label(
        content_frame,
        text=(
            f"\nProbabilidade de vitória do {home_team}: {round(home_win_prob * 100, 2)}%\n"
            f"Odds: {odds_home}\n"
            f"Kelly Criterion para {home_team}: {calculate_kelly_criterion(odds_home, home_win_prob)}%\n"
            f"Valor esperado para {home_team}: {expected_value(home_win_prob, odds_home)}\n"
            f"\nProbabilidade de Empate: {round(draw_prob * 100, 2)}%\n"
            f"Odds: {odds_draw}\n"
            f"Kelly Criterion para Empate: {calculate_kelly_criterion(odds_draw, draw_prob)}%\n"
            f"Valor esperado para Empate: {expected_value(draw_prob, odds_draw)}\n"
            f"\nProbabilidade de vitória do {away_team}: {round(away_win_prob * 100, 2)}%\n"
            f"Odds: {odds_away}\n"
            f"Kelly Criterion para {away_team}: {calculate_kelly_criterion(odds_away, away_win_prob)}%\n"
            f"Valor esperado para {away_team}: {expected_value(away_win_prob, odds_away)}%\n"
        ),
        font=("Arial", 14),
        anchor="center",
        justify="left"
    )
    
    content_frame.pack_propagate(False)  
    content_frame.configure(width=result_label.winfo_reqwidth() + 40, height=result_label.winfo_reqheight() + 40)

    center_window(prediction_window)
    content_frame.place(relx=0.5, rely=0.5, anchor="center")
    
    result_label.pack()
    
    
# Função principal
def main():
    global model, database, teams

    def load_data(liga):
        global database, teams
        if liga == "premier":
            dataset = "premier_matches1724"
            db_file = resource_path("data/dataset.sqlite")  
            teams = premier_league_teams
        elif liga == "brasileirao_a":
            dataset = "brazil_serie_a_matches1724"
            db_file = resource_path("data/dataset.sqlite")    
            teams = brasileirao_a_teams
        elif liga == "brasileirao_b":
            dataset = "brazil_serie_b_matches1724"
            db_file = resource_path("data/dataset.sqlite")   
            teams = brasileirao_b_teams

        con = sqlite3.connect(db_file)
        database = pd.read_sql_query(f"select * from \"{dataset}\"", con)
        con.close()

        train_data(liga)
        home_team_menu['values'] = list(teams)
        away_team_menu['values'] = list(teams)

    def train_data(liga):
        X_train, X_test, y_train, y_test = prepare_data(database, liga)
        global model
        model = train_model(X_train, y_train, liga)

        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        messagebox.showinfo("Treinamento", f"Acurácia do modelo: {accuracy}")

    def predict_data():
        home_team = home_team_var.get()
        away_team = away_team_var.get()
        try:
            odds_home = float(odds_home_entry.get().strip())
            odds_draw = float(odds_draw_entry.get().strip())
            odds_away = float(odds_away_entry.get().strip())

            # Obter dados dos times no banco de dados
            home_data = database[database["home_team_name"] == home_team]
            away_data = database[database["away_team_name"] == away_team]

            match_data = {
                "Pre-Match PPG (Home)": home_data["Pre-Match PPG (Home)"].mean(),
                "Pre-Match PPG (Away)": away_data["Pre-Match PPG (Away)"].mean(),
                "home_ppg": home_data["home_ppg"].mean(),
                "away_ppg": away_data["away_ppg"].mean(),
                "home_team_corner_count": home_data["home_team_corner_count"].mean(),
                "away_team_corner_count": away_data["away_team_corner_count"].mean(),
                "home_team_shots": home_data["home_team_shots"].mean(),
                "away_team_shots": away_data["away_team_shots"].mean(),
                "home_team_shots_on_target": home_data["home_team_shots_on_target"].mean(),
                "away_team_shots_on_target": away_data["away_team_shots_on_target"].mean(),
                "home_team_shots_off_target": home_data["home_team_shots_off_target"].mean(),
                "away_team_shots_off_target": away_data["away_team_shots_off_target"].mean(),
                "home_team_fouls": home_data["home_team_fouls"].mean(),
                "away_team_fouls": away_data["away_team_fouls"].mean(),
                "home_team_possession": home_data["home_team_possession"].mean(),
                "away_team_possession": away_data["away_team_possession"].mean(),
                "Home Team Pre-Match xG": home_data["Home Team Pre-Match xG"].mean(),
                "Away Team Pre-Match xG": away_data["Away Team Pre-Match xG"].mean(),
                "team_a_xg": home_data["team_a_xg"].mean(),
                "team_b_xg": away_data["team_b_xg"].mean(),
                "average_goals_per_match_pre_match": (home_data["average_goals_per_match_pre_match"].mean() + away_data["average_goals_per_match_pre_match"].mean()) / 2,
                "btts_percentage_pre_match": (home_data["btts_percentage_pre_match"].mean() + away_data["btts_percentage_pre_match"].mean()) / 2,
                "average_corners_per_match_pre_match": (home_data["average_corners_per_match_pre_match"].mean() + away_data["average_corners_per_match_pre_match"].mean()) / 2,
                "average_cards_per_match_pre_match": (home_data["average_cards_per_match_pre_match"].mean() + away_data["average_cards_per_match_pre_match"].mean()) / 2,
                "odds_ft_home_team_win": odds_home,
                "odds_ft_draw": odds_draw,
                "odds_ft_away_team_win": odds_away,
                "odds_btts_yes": (home_data["odds_btts_yes"].mean() + away_data["odds_btts_yes"].mean()) / 2,
                "odds_btts_no": (home_data["odds_btts_no"].mean() + away_data["odds_btts_no"].mean()) / 2,
                "home_goals_scored_rolling_avg": home_data["home_goals_scored_rolling_avg"].mean(),
                "home_goals_conceded_rolling_avg": home_data["home_goals_conceded_rolling_avg"].mean(),
                "away_goals_scored_rolling_avg": away_data["away_goals_scored_rolling_avg"].mean(),
                "away_goals_conceded_rolling_avg": away_data["away_goals_conceded_rolling_avg"].mean(),
            }
            
            match_data = pd.DataFrame([match_data], columns=features)
            probabilities = predict_match(model, match_data)
            show_prediction(home_team, away_team, probabilities, odds_home, odds_draw, odds_away)
            clear_fields()

        except ValueError as e:
            messagebox.showerror("Erro", f"Erro:  Preencha adequadamente os campos!")

    def on_league_selected(liga):
        clear_fields()
        load_data(liga)

    def clear_fields():
        home_team_var.set('')
        away_team_var.set('')
        odds_home_entry.delete(0, tk.END)
        odds_draw_entry.delete(0, tk.END)
        odds_away_entry.delete(0, tk.END)

    root = tk.Tk()
    button_font = font.Font(weight="bold", size=10)
    root.title("Previsão de Partidas de Futebol")
    root.geometry("600x400")  # Aumenta o tamanho da janela
    root.configure(bg="#e0e0e0")

    frame = tk.Frame(root, bg="#e0e0e0")
    frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    tk.Label(frame, text="Selecione a Liga:", bg="#e0e0e0").grid(row=0, column=0, pady=10, sticky="w")

    league_frame = tk.Frame(frame, bg="#e0e0e0")
    league_frame.grid(row=1, column=0, pady=5, columnspan=2, sticky="w")
    
    tk.Button(league_frame, text="Premier League", command=lambda: on_league_selected("premier"), bg="#4CAF50", fg="white", font=button_font).grid(row=0, column=0, padx=5)
    tk.Button(league_frame, text="Brasileirão A", command=lambda: on_league_selected("brasileirao_a"), bg="#4CAF50", fg="white", font=button_font).grid(row=0, column=1, padx=5)
    tk.Button(league_frame, text="Brasileirão B", command=lambda: on_league_selected("brasileirao_b"), bg="#4CAF50", fg="white", font=button_font).grid(row=0, column=2, padx=5)

    spacer_frame = tk.Frame(frame, bg="#e0e0e0", height=30)  # Ajuste a altura conforme desejado
    spacer_frame.grid(row=3, column=0, columnspan=2)
    
    tk.Label(frame, text="Time da Casa:", bg="#e0e0e0").grid(row=4, column=0, pady=5, padx=5, sticky="w")
    tk.Label(frame, text="Time Visitante:", bg="#e0e0e0").grid(row=5, column=0, pady=5, padx=5, sticky="w")
    tk.Label(frame, text="Odd Vitória Casa:", bg="#e0e0e0").grid(row=6, column=0, pady=5, padx=5, sticky="w")
    tk.Label(frame, text="Odd Empate:", bg="#e0e0e0").grid(row=7, column=0, pady=5, padx=5, sticky="w")
    tk.Label(frame, text="Odd Vitória Visitante:", bg="#e0e0e0").grid(row=8, column=0, pady=5, padx=5, sticky="w")
    
    home_team_var = tk.StringVar(root)
    away_team_var = tk.StringVar(root)

    home_team_menu = ttk.Combobox(frame, textvariable=home_team_var, values=[], state="readonly", width=29)
    away_team_menu = ttk.Combobox(frame, textvariable=away_team_var, values=[], state="readonly", width=29)

    odds_home_entry = tk.Entry(frame, width=20)
    odds_draw_entry = tk.Entry(frame, width=20)
    odds_away_entry = tk.Entry(frame, width=20)

    home_team_menu.grid(row=4, column=1, pady=5, padx=5, sticky="w")
    away_team_menu.grid(row=5, column=1, pady=5, padx=5, sticky="w")
    odds_home_entry.grid(row=6, column=1, pady=5, padx=5, sticky="w")
    odds_draw_entry.grid(row=7, column=1, pady=5, padx=5, sticky="w")
    odds_away_entry.grid(row=8, column=1, pady=5, padx=5, sticky="w")
    
    tk.Button(frame, text="Fazer Previsão", command=predict_data, bg="#4CAF50", fg="white", font=button_font).grid(row=10, column=0, columnspan=3, pady=30, sticky="e")
    
    center_window(root)
    root.mainloop()

if __name__ == "__main__":
    main()
