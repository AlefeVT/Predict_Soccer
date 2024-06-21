def expected_value(Pwin, odds):
    """
    Calcula o valor esperado (EV) de uma aposta.

    Args:
        Pwin (float): Probabilidade de ganhar a aposta (entre 0 e 1).
        odds (float): Odds decimais da aposta.

    Returns:
        float: Valor esperado da aposta.
    """
    Ploss = 1 - Pwin
    return round((Pwin * (odds - 1)) - (Ploss * 100), 2)
