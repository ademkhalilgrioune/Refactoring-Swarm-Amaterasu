def calculer_age(date_naissance):
    """
    Calcule l'âge en fonction de la date de naissance.

    Args:
        date_naissance (str): Date de naissance au format JJ/MM/AAAA.

    Returns:
        int: L'âge de la personne.
    """
    from datetime import datetime

    # Décomposition de la date de naissance
    jour, mois, annee = map(int, date_naissance.split('/'))

    # Calcul de la date de naissance
    date_naissance = datetime(annee, mois, jour)

    # Calcul de la date actuelle
    date_actuelle = datetime.now()

    # Calcul de l'âge
    age = date_actuelle.year - date_naissance.year

    # Correction de l'âge si la date de naissance n'est pas encore arrivée cette année
    if (date_actuelle.month, date_actuelle.day) < (date_naissance.month, date_naissance.day):
        age -= 1

    return age


def calculer_moyenne(liste_notes):
    """
    Calcule la moyenne d'une liste de notes.

    Args:
        liste_notes (list): Liste de notes.

    Returns:
        float: La moyenne des notes.
    """
    # Vérification si la liste est vide
    if not liste_notes:
        return 0

    # Calcul de la somme des notes
    somme_notes = sum(liste_notes)

    # Calcul de la moyenne
    moyenne = somme_notes / len(liste_notes)

    return moyenne


def division(a, b):
    """
    Effectue une division en vérifiant si le diviseur est nul.

    Args:
        a (float): Le dividende.
        b (float): Le diviseur.

    Returns:
        float: Le résultat de la division.

    Raises:
        ZeroDivisionError: Si le diviseur est nul.
    """
    if b == 0:
        raise ZeroDivisionError("Division par zéro")

    return a / b


# Test de la fonction calculer_age
def test_calculer_age():
    assert calculer_age('12/07/2000') == 23


# Test de la fonction calculer_moyenne
def test_calculer_moyenne():
    assert calculer_moyenne([10, 20, 30]) == 20


# Test de la fonction division
def test_division():
    assert division(10, 2) == 5


# Exécution des tests
if __name__ == '__main__':
    test_calculer_age()
    test_calculer_moyenne()
    test_division()