def calculate_sum(a, b):
    """
    Calcule la somme de deux nombres.

    Args:
        a (int): Le premier nombre.
        b (int): Le deuxième nombre.

    Returns:
        int: La somme des deux nombres.

    Raises:
        TypeError: Si a ou b n'est pas un nombre.
    """
    try:
        if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
            raise TypeError("Les deux arguments doivent être des nombres")
        return a + b
    except TypeError as e:
        print(f"Erreur : {e}")
        return None