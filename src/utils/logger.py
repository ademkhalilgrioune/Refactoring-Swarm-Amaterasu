"""
Module de logging pour le Refactoring Swarm
Enregistre toutes les interactions avec les LLM selon le protocole défini
OBLIGATOIRE pour la note "Qualité des Données" (30% de la note finale)
"""
import json
import os
from datetime import datetime
from enum import Enum
from typing import Dict, Any


class ActionType(Enum):
    """Types d'actions standardisés pour le logging"""
    ANALYSIS = "analysis"      # L'agent analyse le code
    GENERATION = "generation"  # L'agent génère du nouveau contenu
    DEBUG = "debug"           # L'agent analyse une erreur
    FIX = "fix"              # L'agent corrige du code


class Logger:
    def __init__(self, log_file: str = "logs/experiment_data.json"):
        self.log_file = log_file
        
        # Créer le dossier logs si nécessaire
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        # Initialiser le fichier de log
        if not os.path.exists(log_file):
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump([], f)
    
    def log_experiment(
        self,
        agent_name: str,
        model_used: str,
        action: ActionType,
        details: Dict[str, Any],
        status: str = "SUCCESS"
    ):
        """
        Enregistre une interaction avec le LLM.
        
        Args:
            agent_name: Nom de l'agent (ex: "Auditor_Agent")
            model_used: Modèle LLM utilisé
            action: Type d'action (utiliser ActionType enum)
            details: Détails de l'interaction (DOIT contenir input_prompt et output_response)
            status: Statut de l'opération ("SUCCESS" ou "FAILURE")
        """
        # Validation obligatoire
        if "input_prompt" not in details:
            raise ValueError(
                " ERREUR LOGGING: 'input_prompt' manquant dans details. "
                "C'est obligatoire pour la validation scientifique."
            )
        
        if "output_response" not in details:
            raise ValueError(
                " ERREUR LOGGING: 'output_response' manquant dans details. "
                "C'est obligatoire pour la validation scientifique."
            )
        
        # Créer l'entrée de log
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent_name": agent_name,
            "model_used": model_used,
            "action": action.value,
            "status": status,
            "details": details
        }
        
        # Charger les logs existants
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            logs = []
        
        # Ajouter la nouvelle entrée
        logs.append(log_entry)
        
        # Sauvegarder
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)


# Instance globale pour faciliter l'utilisation
_logger = Logger()


def log_experiment(
    agent_name: str,
    model_used: str,
    action: ActionType,
    details: Dict[str, Any],
    status: str = "SUCCESS"
):
    """Fonction helper pour logger facilement"""
    _logger.log_experiment(agent_name, model_used, action, details, status)
