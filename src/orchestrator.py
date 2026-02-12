"""
Orchestrateur du Refactoring Swarm
Coordonne les agents Auditor, Fixer et Judge
"""
import os
from typing import List, Dict
from src.agents.auditor_agent import AuditorAgent
from src.agents.fixer_agent import FixerAgent
from src.agents.judge_agent import JudgeAgent
from src.tools.file_tools import FileManager


class RefactoringOrchestrator:

    def __init__(self, max_iterations: int = 10):
        """
        Initialise l'orchestrateur.
        
        Args:
            max_iterations: Nombre maximum d'itérations de correction
        """
        self.max_iterations = max_iterations
        
        # Initialiser nos agents
        self.auditor = AuditorAgent()
        self.fixer = FixerAgent()
        self.judge = JudgeAgent()
        
        # Gestionnaire de fichiers
        self.file_manager = FileManager()
        
        print("Refactoring Swarm initialisé")
        print(f"   - Max iterations: {max_iterations}")
    
    def process_file(self, file_path: str) -> Dict:
        """
        Traite un fichier Python complet (Audit + Fix + Test).
        
        Args:
            file_path: Chemin du fichier à traiter
        
        Returns:
            Dict avec les résultats du traitement
        """
        print(f"\n{'='*60}")
        print(f" Traitement de: {os.path.basename(file_path)}")
        print(f"{'='*60}")
        
        # Étape 1: Audit du code
        analysis = self.auditor.analyze_file(file_path)
        
        initial_score = analysis['pylint_score']
        print(f" Score initial: {initial_score}/10")
        
        # Boucle de correction itérative
        iteration = 1
        tests_passed = False
        test_results = None
        
        while iteration <= self.max_iterations and not tests_passed:
            print(f"\n Itération {iteration}/{self.max_iterations}")
            
            # Étape 2: Correction du code
            if iteration == 1:
                # Première itération: correction basée sur l'audit
                fix_result = self.fixer.fix_code(analysis, iteration)
            else:
                # Itérations suivantes: correction basée sur les erreurs de tests
                test_errors = test_results['results']['output'] if test_results else None
                fix_result = self.fixer.fix_code(
                    analysis, 
                    iteration, 
                    test_errors=test_errors
                )
            
            # Étape 3: Génération et exécution des tests
            test_results = self.judge.validate_code(file_path)
            tests_passed = test_results['validated']
            
            if tests_passed:
                print(f" Tests passés à l'itération {iteration}!")
                break
            else:
                print(f" Tests échoués à l'itération {iteration}")
                iteration += 1
        
        # Calculer le score final
        final_analysis = self.auditor.analyze_file(file_path)
        final_score = final_analysis['pylint_score']
        
        improvement = final_score - initial_score
        
        result = {
            "file": file_path,
            "initial_score": initial_score,
            "final_score": final_score,
            "improvement": improvement,
            "tests_passed": tests_passed,
            "iterations": iteration,
            "test_results": test_results
        }
        
        print(f"\n Résultats finaux:")
        print(f"   - Itérations: {iteration}")
        
        return result
    
    def process_directory(self, directory: str) -> List[Dict]:
        """
        Traite tous les fichiers Python d'un répertoire.
        
        Args:
            directory: Chemin du répertoire
        
        Returns:
            Liste des résultats pour chaque fichier
        """
        print(f"\n Démarrage du Refactoring Swarm")
        print(f" Répertoire cible: {directory}")
        
        # Lister les fichiers Python
        python_files = self.file_manager.list_python_files(directory)
        
        if not python_files:
            print(f" Aucun fichier Python trouvé dans {directory}")
            return []
        
        print(f" {len(python_files)} fichier(s) Python trouvé(s)")
        
        # Traiter chaque fichier dans sandbox
        results = []
        for i, file_path in enumerate(python_files, 1):
            print(f"\n{'#'*60}")
            print(f"# Fichier {i}/{len(python_files)}")
            print(f"{'#'*60}")
            
            try:
                result = self.process_file(file_path)
                results.append(result)
            except Exception as e:
                print(f" Erreur fatale sur {file_path}: {e}")
                results.append({
                    "file": file_path,
                    "error": str(e),
                    "tests_passed": False
                })
        
        
        print(f"\n{'='*60}")
        print(f" RÉSUMÉ GLOBAL")
        print(f"{'='*60}")
        
        total = len(results)
        passed = sum(1 for r in results if r.get('tests_passed', False))
        
        print(f" Fichiers validés: {passed}/{total}")
        

        
        return results
