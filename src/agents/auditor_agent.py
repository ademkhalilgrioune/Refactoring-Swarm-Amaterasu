"""
Agent Auditor - Analyse le code et produit un plan de refactoring
pour comprendre l'INTENTION même sans documentation
"""
import json
from typing import Dict
from src.utils.llm_client import LLMClient
from src.utils.logger import log_experiment, ActionType
from src.tools.file_tools import FileManager, CodeAnalyzer


class AuditorAgent:
    """
    Agent qui est responsable de l'analyse du code source
    Détecte les problèmes et crée un plan de refactoring
    """
    
    def __init__(self):
        """Initialise l'agent Auditor"""
        self.name = "Auditor_Agent"
        self.llm = LLMClient()
        self.file_manager = FileManager()
        self.analyzer = CodeAnalyzer()
    
    def analyze_file(self, file_path: str) -> Dict:
        """
        Analyse un fichier Python et génère un rapport de problèmes.
        
        Args:
            file_path: Chemin du fichier à analyser
        
        Returns:
            Dict contenant le plan de refactoring
        """
        print(f"\n [{self.name}] Analyse de {file_path}...")
        
        # Lire le code
        code_content = self.file_manager.read_file(file_path)
        
        # Exécuter Pylint
        pylint_results = self.analyzer.run_pylint(file_path)
        
        # Construire le prompt système - CRUCIAL pour la qualité et linformer par l ai croq
        system_prompt = """Tu es un expert Python spécialisé dans l'audit de code et le refactoring.
Ta mission est d'analyser du code Python de mauvaise qualité et de produire un plan de refactoring détaillé.


1. Analyse les NOMS des fonctions/variables pour comprendre l'INTENTION du code
2. Même sans doc, devine ce que le code DEVRAIT faire (pas ce qu'il fait)
3. Identifie TOUS les problèmes: bugs, mauvaises pratiques, code smell, manque de documentation
4. Priorise les problèmes par gravité (CRITIQUE > MAJEUR > MINEUR)
5. Propose des solutions concrètes pour chaque problème
6. Sois concis mais précis

EXEMPLE CRUCIAL:
Si une fonction s'appelle "calculate_discount" mais additionne au lieu de soustraire,
tu dois détecter que l'INTENTION est une réduction, pas une addition!

FORMAT DE SORTIE (JSON):
{
  "file_path": "chemin/du/fichier.py",
  "quality_score": 3.5,
  "issues": [
    {
      "severity": "CRITIQUE|MAJEUR|MINEUR",
      "line": 42,
      "type": "bug|code_smell|documentation|style|logic_error",
      "description": "Description du problème",
      "solution": "Comment le corriger",
      "expected_behavior": "Ce que le code DEVRAIT faire (basé sur les noms)"
    }
  ],
  "refactoring_plan": "Plan général de refactoring en 3-5 étapes",
  "estimated_effort": "FAIBLE|MOYEN|ÉLEVÉ"
}
"""
        
        # Prompt utilisateur avec le code
        user_prompt = f"""Analyse ce fichier Python et produis un plan de refactoring détaillé.

FICHIER: {file_path}

CODE SOURCE:
```python
{code_content}
```

RAPPORT PYLINT (Score: {pylint_results['score']}/10):
{pylint_results['raw_output'][:1000]}

INSTRUCTIONS SPÉCIALES:
- Regarde les noms de fonctions/variables pour deviner l'intention
- Si "calculate_average" retourne une somme, c'est un BUG LOGIQUE
- Si "is_adult" n'a pas de seuil clair, propose 18 ans (standard)
- Détecte les bugs de logique métier, pas juste la syntaxe

Produis une analyse complète au format JSON demandé."""
        
        try:
            # Appel au LLM client
            response = self.llm.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.3  # Bas pour être déterministe
            )
            
            # Extraire le JSON de la réponse
            response_text = response
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            
            # Parser le JSON
            try:
                analysis_result = json.loads(response_text)
            except json.JSONDecodeError:
                # Si le parsing échoue, créer une structure par défaut
                analysis_result = {
                    "file_path": file_path,
                    "quality_score": pylint_results['score'],
                    "issues": [{
                        "severity": "MAJEUR",
                        "type": "parsing",
                        "description": "Impossible de parser la réponse du LLM",
                        "solution": "Réessayer l'analyse"
                    }],
                    "refactoring_plan": response_text,
                    "estimated_effort": "MOYEN"
                }
            
            # Logger l'interaction
            log_experiment(
                agent_name=self.name,
                model_used=self.llm.get_model_name(),
                action=ActionType.ANALYSIS,
                details={
                    "file_analyzed": file_path,
                    "input_prompt": user_prompt[:500] + "...",
                    "output_response": response[:500] + "...",
                    "pylint_score": pylint_results['score'],
                    "issues_count": len(analysis_result.get('issues', []))
                },
                status="SUCCESS"
            )
            
            print(f"✓ Analyse terminée: {len(analysis_result.get('issues', []))} problème(s) trouvé(s)")
            return {
                "file": file_path,
                "analysis": analysis_result,
                "pylint_score": pylint_results['score'],
                "raw_code": code_content
            }
        
        except Exception as e:
            print(f"✗ Erreur lors de l'analyse: {e}")
            
            # Logger les echecs
            log_experiment(
                agent_name=self.name,
                model_used=self.llm.get_model_name(),
                action=ActionType.ANALYSIS,
                details={
                    "file_analyzed": file_path,
                    "input_prompt": user_prompt[:500] + "...",
                    "output_response": f"ERREUR: {str(e)}",
                    "error": str(e)
                },
                status="FAILURE"
            )
            
            return {
                "file": file_path,
                "analysis": {
                    "file_path": file_path,
                    "quality_score": 0.0,
                    "issues": [],
                    "refactoring_plan": f"Erreur d'analyse: {str(e)}",
                    "estimated_effort": "INCONNU"
                },
                "pylint_score": 0.0,
                "raw_code": code_content
            }
