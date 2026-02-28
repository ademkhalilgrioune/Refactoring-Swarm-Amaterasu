x = 10

def est_dans_interval(z: int) -> bool:
    """
    Vérifie si la valeur z est comprise entre 0 et 100 (0 < z < 100).

    Args:
        z (int): La valeur à vérifier.

    Returns:
        bool: True si z est dans l'intervalle, False sinon.

    Raises:
        ZeroDivisionError: Si z est utilisé dans une division par zéro.
        TypeError: Si z n'est pas un entier.
    """
    if not isinstance(z, int):
        raise TypeError("La valeur z doit être un entier.")
    try:
        if z > 0 and z < 100:
            return True
    except ZeroDivisionError:
        raise ZeroDivisionError("Erreur de division par zéro.")
    return False