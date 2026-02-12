"""
Agent Fixer - Corrige le code selon le plan de refactoring
"""
from typing import Dict, Optional
from src.utils.llm_client import LLMClient
from src.utils.logger import log_experiment, ActionType
from src.tools.file_tools import FileManager, extract_code_block


class FixerAgent:
    """
    Agent responsable de la correction du code
    Applique les modifications basées sur le plan de l'Auditor
    """
    
    def __init__(self):
        """Initialise l'agent Fixer"""
        self.name = "Fixer_Agent"
        self.llm = LLMClient()
        self.file_manager = FileManager()
    
    def fix_code(
        self, 
        analysis: Dict,
        iteration: int = 1,
        test_errors: Optional[str] = None
    ) -> Dict:
        """
        Corrige le code basé sur l'analyse de l'Auditor.
        
        Args:
            analysis: Résultat de l'analyse de l'Auditor
            iteration: Numéro de l'itération
            test_errors: Erreurs de tests (si disponibles)
        
        Returns:
            Dict avec le code corrigé
        """
        file_path = analysis['file']
        original_code = analysis['raw_code']
        audit_report = analysis['analysis']
        
        print(f"\n [{self.name}] Correction de {file_path} (Itération {iteration})...")
        
        # Construction du prompt système
        system_prompt = """Tu es un expert Python spécialisé dans le refactoring de code.
Ta mission est de corriger le code Python selon le plan de refactoring fourni.

RÈGLES CRITIQUES:
1. Corriger TOUS les bugs identifiés
2. Améliorer la lisibilité et la maintenabilité
3. Ajouter des docstrings complètes (Google style)
4. Respecter les conventions PEP8
5. Conserver la MÊME fonctionnalité - ne pas changer la logique métier
6. Le code doit être EXÉCUTABLE et SANS ERREUR

RÈGLE D'OR (Prof. BATATA):
Si le code DEVRAIT faire X (basé sur les noms) mais fait Y, corrige pour faire X!
Exemple: "calculate_discount" doit SOUSTRAIRE, pas additionner!

FORMAT DE SORTIE:
Retourne UNIQUEMENT le code Python corrigé, sans explications ni markdown.
"""
        
        # Construction des informations du contexte
        issues_summary = "\n".join([
            f"- [{issue.get('severity', 'MINEUR')}] Ligne {issue.get('line', '?')}: {issue.get('description', 'N/A')}"
            for issue in audit_report.get('issues', [])[:10]
        ])
        
        refactoring_plan = audit_report.get('refactoring_plan', 'Aucun plan fourni')
        
        # Prompt utilisateur
        user_prompt = f"""Corrige ce code Python selon le plan de refactoring.

FICHIER: {file_path}

CODE ORIGINAL:
```python
{original_code}
```

PROBLÈMES IDENTIFIÉS:
{issues_summary}

PLAN DE REFACTORING:
{refactoring_plan}
"""
        
        # Ajouter les erreurs de tests si disponibles
        if test_errors:
            user_prompt += f"""

 ERREURS DE TESTS À CORRIGER:
{test_errors}

IMPORTANT: Le code doit passer ces tests !
Analyse les assertions pour comprendre le comportement attendu.
"""
        
        user_prompt += "\n\nRetourne le code Python corrigé complet (sans markdown, juste le code)."
        
        try:
            # Appel au LLM
            response = self.llm.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.4  
            )
            
            # Extraire le code
            fixed_code = extract_code_block(response)
            
            # Écrire le code corrigé
            self.file_manager.write_file(file_path, fixed_code)
            
            # Logger l'interaction
            log_experiment(
                agent_name=self.name,
                model_used=self.llm.get_model_name(),
                action=ActionType.FIX if not test_errors else ActionType.DEBUG,
                details={
                    "file_fixed": file_path,
                    "iteration": iteration,
                    "input_prompt": user_prompt[:500] + "...",
                    "output_response": response[:500] + "...",
                    "original_code_length": len(original_code),
                    "fixed_code_length": len(fixed_code),
                    "had_test_errors": test_errors is not None
                },
                status="SUCCESS"
            )
            
            print(f" Code corrigé: {len(fixed_code)} caractères")
            return {
                "file": file_path,
                "fixed_code": fixed_code,
                "iteration": iteration
            }
        
        except Exception as e:
            print(f" Erreur lors de la correction: {e}")
            
            # Logger les échecs
            log_experiment(
                agent_name=self.name,
                model_used=self.llm.get_model_name(),
                action=ActionType.FIX,
                details={
                    "file_fixed": file_path,
                    "iteration": iteration,
                    "input_prompt": user_prompt[:500] + "...",
                    "output_response": f"ERREUR: {str(e)}",
                    "error": str(e)
                },
                status="FAILURE"
            )
            
            return {
                "file": file_path,
                "fixed_code": original_code,
                "iteration": iteration,
                "error": str(e)
            }
