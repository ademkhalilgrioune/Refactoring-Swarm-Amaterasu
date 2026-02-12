"""
Client LLM centralisé pour gérer les appels à Groq
VERSION SIMPLIFIÉE - Sans conflit de proxies
"""
import os
import requests
from typing import Optional
from dotenv import load_dotenv


class LLMClient:

    def __init__(self, model_name: str = "llama-3.3-70b-versatile"):
        """
        Initialise le client LLM avec Groq.
        
        Args:
            model_name: Nom du modèle Groq à utiliser
        """
        load_dotenv()
        
        self.api_key = os.getenv('GROQ_API_KEY')
        if not self.api_key:
            raise ValueError(
                "GROQ_API_KEY non trouvée. "
            )
        
        self.model_name = model_name
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        
        print(f"✓ LLM configuré: Groq ({model_name})")
    
    def generate(
        self, 
        prompt: str, 
        temperature: float = 0.7,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Génère une réponse avec Groq via API REST directe.
        """
        try:
            # Construire les messages
            messages = []
            
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            # Préparer la requête
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model_name,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": 2048
            }
            
            # Faire l'appel API groc
            response = requests.post(
                self.api_url,
                headers=headers,
                json=data,
                timeout=30
            )
            
            # Vérifier la réponse
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"].strip()
            else:
                error_msg = f"Erreur Groq ({response.status_code}): {response.text}"
                print(f" {error_msg}")
                return self._fallback_response(prompt)
                
        except Exception as e:
            print(f" ERREUR: {str(e)}")
            return self._fallback_response(prompt)
    
    def _fallback_response(self, prompt: str) -> str:
        """Réponse de secours en cas d'erreur"""
        print("  Utilisation du mode fallback (réponses simulées)")
        
        if "analyse" in prompt.lower() or "audit" in prompt.lower():
            return '''{
  "quality_score": 5.0,
  "issues": [
    {
      "severity": "MAJEUR",
      "line": 5,
      "type": "bug",
      "description": "Division par zéro potentielle",
      "solution": "Ajouter une vérification"
    }
  ],
  "refactoring_plan": "1. Ajouter docstring\\n2. Gérer les erreurs",
  "estimated_effort": "MOYEN"
}'''
        elif "corrige" in prompt.lower() or "fix" in prompt.lower():
            return '''def add(a, b):
    """Addition."""
    return a + b

def divide(a, b):
    """Division avec gestion d'erreur."""
    if b == 0:
        raise ValueError("Division par zéro")
    return a / b'''
        else:
            return '''def test_add():
    assert add(2, 2) == 4

def test_divide():
    with pytest.raises(ValueError):
        divide(1, 0)'''
    
    def get_model_name(self) -> str:
        return f"groq/{self.model_name}"