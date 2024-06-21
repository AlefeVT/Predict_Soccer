def expected_value(probability, odds):
    """
    Calcula o valor esperado (EV) de uma aposta.

    Args:
        Pwin (float): Probabilidade de ganhar a aposta (entre 0 e 1).
        odds (float): Odds decimais da aposta.

    Returns:
        float: Valor esperado da aposta.
    """
    return round((probability * (odds - 1) - (1 - probability)) * 100, 2)