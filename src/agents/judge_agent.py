"""
Agent Judge - Génère et exécute des tests unitaires dynamiquement
pas juste l'exécution sans crash!
"""
from typing import Dict
from src.utils.llm_client import LLMClient
from src.utils.logger import log_experiment, ActionType
from src.tools.file_tools import FileManager, TestRunner, extract_code_block


class JudgeAgent:
    """
    Agent responsable de la génération et validation des tests
    Crée des tests unitaires dynamiquement avec Gemini et vérifie que le code fonctionne
    """
    
    def __init__(self):
        """Initialise l'agent Judge"""
        self.name = "Judge_Agent"
        self.llm = LLMClient()
        self.file_manager = FileManager()
        self.test_runner = TestRunner()
    
    def generate_tests(self, file_path: str) -> str:
        """
        Génère dynamiquement des tests unitaires pour un fichier Python.
        
        Args:
            file_path: Chemin du fichier à tester
        
        Returns:
            Chemin du fichier de test créé
        """
        print(f"\n [{self.name}] Génération des tests pour {file_path}...")
        
        # Lire le code
        code_content = self.file_manager.read_file(file_path)
        
        # Construire le prompt système 
        system_prompt = """Tu es un expert en tests unitaires Python avec pytest.
Ta mission est de générer des tests unitaires complets pour valider le code fourni.


COMMENT DEVINER LE COMPORTEMENT ATTENDU:
1. Analyse les NOMS de fonctions/variables
   - "calculate_average" → doit retourner la moyenne, pas la somme
   - "is_adult(18)" → doit retourner True (seuil standard)
   - "calculate_discount" → doit RÉDUIRE le prix, pas l'augmenter

2. Utilise la logique métier évidente
   - Une remise doit donner un prix INFÉRIEUR
   - Une moyenne de [10, 20] doit être 15
   - Un filtre doit exclure/inclure selon le critère

3. Si ambiguïté, choisis le comportement le plus logique/standard

RÈGLES DE TESTS:
1. Utilise pytest comme framework de test
2. Teste TOUTES les fonctions publiques
3. Inclus des cas normaux, limites et erreurs
4. Utilise des assertions claires qui vérifient la LOGIQUE
5. Ajoute des docstrings aux fonctions de test
6. Nomme les tests de façon descriptive (test_fonction_cas)

EXEMPLE CRUCIAL:
```python
# Si le code contient:
def calculate_discount(price, percent):
    return price + (price * percent / 100)  # BUG: additionne au lieu de soustraire

# Ton test DOIT être:
def test_calculate_discount_reduces_price():
    \"\"\"Une remise doit RÉDUIRE le prix\"\"\"
    assert calculate_discount(100, 10) == 90  # 10% de remise
    assert calculate_discount(50, 20) < 50    # Le prix final doit être inférieur
```

FORMAT DE SORTIE:
Retourne UNIQUEMENT le code Python des tests, sans explications ni markdown.
Le fichier doit commencer par les imports nécessaires."""
        
        # Prompt utilisateur
        user_prompt = f"""Génère des tests unitaires complets pour ce code Python.

FICHIER SOURCE: {file_path}

CODE À TESTER:
```python
{code_content}
```

EXIGENCES CRITIQUES:
- Utilise pytest
- Teste toutes les fonctions et classes
- Les tests doivent valider la LOGIQUE MÉTIER basée sur les noms
- Inclus des cas normaux, limites et d'erreur
- Les tests doivent Ãªtre immédiatement exécutables

IMPORTANT:
Regarde les NOMS pour deviner le comportement attendu.
Si "calculate_average", le test doit vérifier une MOYENNE, pas une somme!
Si "is_adult", utilise le seuil standard de 18 ans.
Si "calculate_discount", vérifie que le prix DIMINUE.

Génère au minimum 5-10 tests pertinents.
Retourne uniquement le code Python (sans markdown)."""
        
        try:
            # Appel au LLM pour générer les tests
            response = self.llm.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.5  # Un peu de créativité pour les cas de test
            )
            
            # Extraire le code de test
            test_code = extract_code_block(response)
            
            # Créer le fichier de test
            test_file = self.test_runner.create_test_file(file_path, test_code)
            
            # Logger l'interaction
            log_experiment(
                agent_name=self.name,
                model_used=self.llm.get_model_name(),
                action=ActionType.GENERATION,
                details={
                    "file_tested": file_path,
                    "test_file_created": test_file,
                    "input_prompt": user_prompt[:500] + "...",
                    "output_response": response[:500] + "...",
                    "source_code_length": len(code_content),
                    "test_code_length": len(test_code)
                },
                status="SUCCESS"
            )
            
            print(f"✓ Tests générés: {test_file}")
            return test_file
        
        except Exception as e:
            print(f"✗ Erreur lors de la génération des tests: {e}")
            
            # Logger l'échec
            log_experiment(
                agent_name=self.name,
                model_used=self.llm.get_model_name(),
                action=ActionType.GENERATION,
                details={
                    "file_tested": file_path,
                    "input_prompt": user_prompt[:500] + "...",
                    "output_response": f"ERREUR: {str(e)}",
                    "error": str(e)
                },
                status="FAILURE"
            )
            
            return None
    
    def run_tests(self, test_file: str) -> Dict:
        """
        Exécute les tests unitaires.
        
        Args:
            test_file: Chemin du fichier de test
        
        Returns:
            Résultats des tests
        """
        print(f" Exécution des tests: {test_file}")
        
        results = self.test_runner.run_tests(test_file)
        
        if results['success']:
            print(f" Tous les tests passent! ({results['passed']}/{results['total']})")
        else:
            print(f" Tests échoués: {results['failed']}/{results['total']}")
        
        return results
    
    def validate_code(self, file_path: str) -> Dict:
        """
        Génère les tests dynamiquement et les exécute pour valider le code.
        
        Args:
            file_path: Chemin du fichier à valider
        
        Returns:
            Dict avec les résultats de validation
        """
        # Générer les tests dynamiquement avec Gemini
        test_file = self.generate_tests(file_path)
        
        if not test_file:
            return {
                "file": file_path,
                "test_file": None,
                "results": {
                    'passed': 0,
                    'failed': 0,
                    'total': 0,
                    'success': False,
                    'output': 'Échec de la génération des tests'
                },
                "validated": False
            }
        
        # Exécuter les tests
        results = self.run_tests(test_file)
        
        return {
            "file": file_path,
            "test_file": test_file,
            "results": results,
            "validated": results['success']
        }
