def count_down(n):
    """
    Cette fonction affiche les nombres de n à 1 en décrémentant.

    Args:
        n (int): Le nombre de départ pour le décompte.

    Returns:
        None
    """
    while n > 0:
        print(n)
        n -= 1  # Correction du bug : n diminue à chaque itération

def test_count_down(capsys):
    """
    Test unitaire pour la fonction count_down.

    Vérifie que la fonction affiche les nombres de n à 1.
    """
    count_down(3)
    captured = capsys.readouterr()
    assert captured.out == "3\n2\n1\n"

def test_count_down_zero(capsys):
    """
    Test unitaire pour la fonction count_down avec n = 0.

    Vérifie que la fonction ne affiche rien lorsque n est 0.
    """
    count_down(0)
    captured = capsys.readouterr()
    assert captured.out == ""

def test_count_down_negatif(capsys):
    """
    Test unitaire pour la fonction count_down avec n < 0.

    Vérifie que la fonction ne affiche rien lorsque n est négatif.
    """
    count_down(-1)
    captured = capsys.readouterr()
    assert captured.out == ""

import pytest