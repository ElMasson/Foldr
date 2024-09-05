#advanced_response_generation/compile_final_response.py

from typing import Dict
from .utils import query_llm

def compile_final_response(question: str, critique: str, context: str, initial_response: str,
                           additional_research: Dict[str, str]) -> str:
    """
    Compile une réponse finale détaillée en utilisant toutes les informations disponibles.

    Args:
        question (str): La question originale.
        critique (str): La critique de la réponse initiale.
        context (str): Le contexte de la subvention.
        initial_response (str): La réponse initiale à la question.
        additional_research (Dict[str, str]): Les résultats des recherches supplémentaires.

    Returns:
        str: La réponse finale compilée.
    """
    research_summary = "\n\n".join([f"Question: {q}\nRéponse: {r}" for q, r in additional_research.items()])

    prompt = f"""
    En tant qu'expert en rédaction de demandes de subvention, rédigez une réponse complète et détaillée à la question suivante. Utilisez toutes les informations fournies pour créer une réponse optimale qui répond pleinement à la question et satisfait aux critères de la subvention.

    Question originale : {question}

    Critique de la réponse initiale : {critique}

    Contexte de la subvention : {context}

    Réponse initiale : {initial_response}

    Recherches supplémentaires :
    {research_summary}

    Votre réponse doit :
    1. Répondre directement et complètement à la question posée
    2. Intégrer les points forts de la réponse initiale
    3. Adresser les points d'amélioration mentionnés dans la critique
    4. Incorporer les informations pertinentes des recherches supplémentaires
    5. Être alignée avec les objectifs et les critères de la subvention
    6. Être claire, structurée et convaincante
    7. Utiliser des exemples concrets et des données spécifiques pour étayer vos arguments

    Rédigez maintenant une réponse complète et détaillée :
    """

    return query_llm(prompt)