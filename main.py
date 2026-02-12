"""
Point d'entrée principal du Refactoring Swarm
Utilisation: python main.py --target_dir ./sandbox/dataset
"""
import argparse
import os
import sys
from src.orchestrator import RefactoringOrchestrator


def main():
    """Fonction principale"""

    # Parser les arguments de ligne de commande qaund on tape
    parser = argparse.ArgumentParser(
        description="Refactoring Swarm - Système multi-agents de refactoring automatique"
    )
    parser.add_argument(
        '--target_dir',
        type=str,
        required=True,
        help="Répertoire contenant le code à refactoriser"
    )
    parser.add_argument(
        '--max_iterations',
        type=int,
        default=10,
        help="Nombre maximum d'itérations de correction (défaut: 10)"
    )
    
    args = parser.parse_args()
    
    # Vérifier que le répertoire existe
    if not os.path.exists(args.target_dir):
        print(f" ERREUR: Le répertoire '{args.target_dir}' n'existe pas!")
        sys.exit(1)
    
    if not os.path.isdir(args.target_dir):
        print(f" ERREUR: '{args.target_dir}' n'est pas un répertoire!")
        sys.exit(1)
    
    # Créer l'orchestrateur
    try:
        orchestrator = RefactoringOrchestrator(max_iterations=args.max_iterations)
    except ValueError as e:
        print(f" ERREUR DE CONFIGURATION: {e}")
        print("\n Avez-vous créé le fichier .env avec votre GOOGLE_API_KEY?")
        sys.exit(1)
    
    # Lancer le processus de refactoring notre application
    try:
        results = orchestrator.process_directory(args.target_dir)
        
        # Code de sortie basé sur les résultats
        if not results:
            sys.exit(1)  # Aucun fichier traité logiquement 
        
        # Succès si au moins 50% des fichiers passent les tests
        success_rate = sum(1 for r in results if r.get('tests_passed', False)) / len(results)
        if success_rate >= 0.5:
            sys.exit(0)  # Succès
        else:
            sys.exit(2)  # Échec partiel
    
    except KeyboardInterrupt:
        print("\n\n Interruption par l'utilisateur")
        sys.exit(130)
    
    except Exception as e:
        print(f"\n ERREUR FATALE: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
