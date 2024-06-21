def calculate_kelly_criterion(odds, model_prob):
    """
    Calculates the fraction of the bankroll to be wagered on each bet
    """
    bankroll_fraction = round((100 * (odds * model_prob - (1 - model_prob))) / odds, 2)
    return bankroll_fraction if bankroll_fraction > 0 else 0
