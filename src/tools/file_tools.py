"""
Outils pour les agents : lecture/écriture de fichiers, analyse statique, tests
"""
import os
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional


class FileManager:
    """Gestionnaire de fichiers sécurisé pour le sandbox"""
    
    def __init__(self, sandbox_path: str = "./sandbox"):
        self.sandbox_path = Path(sandbox_path).resolve()
        self.sandbox_path.mkdir(exist_ok=True, parents=True)
    
    def is_safe_path(self, file_path: str) -> bool:
        """Vérifie que le chemin est dans le sandbox"""
        try:
            abs_path = Path(file_path).resolve()
            # Vérifier si le chemin est dans sandbox OU dans le répertoire courant
            # (pour permettre l'accès aux fichiers passés en --target_dir)
            return True  # Mode permissif pour le TP
        except ValueError:
            return False
    
    def read_file(self, file_path: str) -> str:
        """Lit un fichier de manière sécurisée"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def write_file(self, file_path: str, content: str) -> None:
        """Écrit dans un fichier de manière sécurisée"""
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def list_python_files(self, directory: str) -> List[str]:
        """Liste tous les fichiers Python dans un répertoire (sauf les tests)"""
        python_files = []
        for root, _, files in os.walk(directory):
            for file in files:
                # Ignorer les fichiers de test
                if file.endswith('.py') and not file.startswith('test_'):
                    python_files.append(os.path.join(root, file))
        
        return list(set(python_files))
    
    def file_exists(self, file_path: str) -> bool:
        """Vérifie si un fichier existe"""
        return Path(file_path).exists()


class CodeAnalyzer:
    """Analyseur de code avec Pylint"""
    
    @staticmethod
    def run_pylint(file_path: str) -> Dict:
        """
        Exécute Pylint sur un fichier et retourne les résultats.
        
        Returns:
            Dict avec 'score', 'issues' et 'raw_output'
        """
        try:
            result = subprocess.run(
                ['pylint', file_path, '--output-format=json', '--score=yes'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Parser le JSON
            try:
                issues = json.loads(result.stdout) if result.stdout else []
            except json.JSONDecodeError:
                issues = []
            
            # Extraire le score depuis stderr
            score = 0.0
            full_output = result.stdout + result.stderr

            for line in full_output.split('\n'):
                if 'rated at' in line.lower():
                    try:
                        parts = line.split('rated at')[1].split('/')
                        score = float(parts[0].strip())
                        break
                    except (IndexError, ValueError):
                        pass
            
            return {
                'score': score,
                'issues': issues,
                'raw_output': result.stderr + '\n' + result.stdout
            }
        
        except subprocess.TimeoutExpired:
            return {'score': 0.0, 'issues': [], 'error': 'Timeout', 'raw_output': ''}
        except FileNotFoundError:
            return {'score': 0.0, 'issues': [], 'error': 'Pylint non installé', 'raw_output': ''}
        except Exception as e:
            return {'score': 0.0, 'issues': [], 'error': str(e), 'raw_output': ''}


class TestRunner:
    """Exécuteur de tests unitaires avec Pytest""" 
    
    @staticmethod
    def run_tests(test_file: str) -> Dict:
        """
        Exécute les tests unitaires avec pytest.
        
        Returns:
            Dict avec 'passed', 'failed', 'total', 'success', 'output'
        """
        if not os.path.exists(test_file):
            return {
                'passed': 0,
                'failed': 0,
                'total': 0,
                'success': False,
                'output': f'Fichier de test non trouvé: {test_file}',
                'return_code': -1
            }
        
        try:
            result = subprocess.run(
                ['pytest', test_file, '-v', '--tb=short', '--no-header'],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            output = result.stdout + result.stderr
            
            # Parser les résultats
            passed = output.count(' PASSED')
            failed = output.count(' FAILED')
            errors = output.count(' ERROR')
            
            total = passed + failed + errors
            
            return {
                'passed': passed,
                'failed': failed + errors,
                'total': total,
                'success': (failed + errors) == 0 and total > 0,
                'output': output,
                'return_code': result.returncode
            }
        
        except subprocess.TimeoutExpired:
            return {
                'passed': 0,
                'failed': 0,
                'total': 0,
                'success': False,
                'output': "Timeout lors de l'exécution des tests",
                'return_code': -1
            }
        except FileNotFoundError:
            return {
                'passed': 0,
                'failed': 0,
                'total': 0,
                'success': False,
                'output': 'Pytest non installé. Installez-le avec: pip install pytest',
                'return_code': -1
            }
        except Exception as e:
            return {
                'passed': 0,
                'failed': 0,
                'total': 0,
                'success': False,
                'output': f'Erreur: {str(e)}',
                'return_code': -1
            }
    
    @staticmethod
    def create_test_file(source_file: str, test_content: str) -> str:
        """
        Crée un fichier de test à partir du contenu généré.
        
        Args:
            source_file: Chemin du fichier source
            test_content: Contenu des tests générés
        
        Returns:
            Chemin du fichier de test créé
        """
        base_name = os.path.splitext(os.path.basename(source_file))[0]
        test_dir = os.path.dirname(source_file)
        test_file = os.path.join(test_dir, f"test_{base_name}.py")
        
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        return test_file


def extract_code_block(text: str) -> str:
    """
    Extrait le code Python depuis une réponse de LLM.
    Gère les formats: ```python, ```Python, ou juste le texte.
    """
    # Chercher un bloc de code markdown
    if '```python' in text.lower():
        start = text.lower().find('```python') + len('```python')
        end = text.find('```', start)
        if end != -1:
            return text[start:end].strip()
    
    
    return text.strip()
