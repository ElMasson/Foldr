import os
from openai import OpenAI
from typing import List, Dict
from config.config import OPENAI_API_KEY


client = OpenAI(api_key=OPENAI_API_KEY)

def query_llm(prompt: str, model: str = "gpt-4o-mini") -> str:
    """
    Fonction utilitaire pour interroger le modèle LLM.
    """
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "Vous êtes un assistant expert en analyse de demandes de subvention."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000,
        temperature=0
    )
    return response.choices[0].message.content

def extract_key_points(text: str) -> List[str]:
    """
    Extrait les points clés d'un texte donné.
    """
    prompt = f"Extrayez les points clés du texte suivant sous forme de liste :\n\n{text}"
    response = query_llm(prompt)
    return [point.strip() for point in response.split('\n') if point.strip()]

def merge_responses(responses: List[str]) -> str:
    """
    Fusionne plusieurs réponses en une seule réponse cohérente.
    """
    prompt = f"Fusionnez les réponses suivantes en un texte cohérent :\n\n" + "\n\n".join(responses)
    return query_llm(prompt)