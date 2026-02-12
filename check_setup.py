"""
Script de vérification de l'environnement
VERSION GROQ
"""
import sys
import os

def check_python_version():
    """Vérifie la version de Python"""
    version = sys.version_info
    if version.major == 3 and version.minor in [10, 11]:
        print("✅ Python version OK:", f"{version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor} détecté. Requis: 3.10 ou 3.11")
        return False

def check_module(module_name, package_name=None):
    """Vérifie qu'un module est installé"""
    if package_name is None:
        package_name = module_name
    
    try:
        __import__(module_name)
        print(f"✅ {package_name} installé")
        return True
    except ImportError:
        print(f"❌ {package_name} manquant - Installez avec: pip install {package_name}")
        return False

def check_env_file():
    """Vérifie que le fichier .env existe"""
    if os.path.exists('.env'):
        print("✅ Fichier .env trouvé")
        return True
    else:
        print("❌ Fichier .env manquant")
        print("   Créez-le à partir de .env.example")
        return False

def check_groq_api_key():
    """Vérifie que la clé API Groq est configurée"""
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('GROQ_API_KEY')
    if api_key and api_key != 'votre_cle_groq_ici':
        print("✅ GROQ_API_KEY configurée")
        return True
    else:
        print("❌ GROQ_API_KEY non configurée dans .env")
        print("   Obtenez une clé gratuite sur: https://console.groq.com/keys")
        return False

def check_directory_structure():
    """Vérifie la structure des dossiers"""
    required_dirs = ['src', 'src/agents', 'src/tools', 'src/utils', 'logs', 'sandbox']
    all_ok = True
    
    for dir_path in required_dirs:
        if os.path.isdir(dir_path):
            print(f"✅ Dossier {dir_path}/ existe")
        else:
            print(f"❌ Dossier {dir_path}/ manquant")
            all_ok = False
    
    return all_ok

def main():
    """Fonction principale de vérification"""
    print("="*60)
    print("🔍 VÉRIFICATION DE L'ENVIRONNEMENT (VERSION GROQ)")
    print("="*60)
    
    checks = []
    
    print("\n📌 Version Python:")
    checks.append(check_python_version())
    
    print("\n📦 Modules Python:")
    checks.append(check_module('dotenv', 'python-dotenv'))
    checks.append(check_module('groq'))
    checks.append(check_module('pylint'))
    checks.append(check_module('pytest'))
    
    print("\n📁 Structure de dossiers:")
    checks.append(check_directory_structure())
    
    print("\n🔑 Configuration API:")
    checks.append(check_env_file())
    if checks[-1]:  # Si .env existe
        checks.append(check_groq_api_key())
    
    print("\n" + "="*60)
    if all(checks):
        print("✅ ENVIRONNEMENT OK - Vous pouvez commencer !")
        print("="*60)
        return 0
    else:
        print("❌ PROBLÈMES DÉTECTÉS - Corrigez-les avant de continuer")
        print("="*60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
