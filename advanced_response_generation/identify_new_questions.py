#advanced_response_generation/identify_new_questions.py

from typing import List
from .utils import query_llm, extract_key_points

def identify_new_questions(critique: str, context: str, initial_response: str) -> List[str]:
    """
    Identifie de nouvelles questions pertinentes basées sur la critique, le contexte et la réponse initiale.

    Args:
        critique (str): La critique de la réponse initiale.
        context (str): Le contexte de la subvention.
        initial_response (str): La réponse initiale à la question.

    Returns:
        List[str]: Une liste de nouvelles questions pertinentes.
    """
    prompt = f"""
    En vous basant sur la critique, le contexte et la réponse initiale suivants, identifiez de nouvelles questions pertinentes pour approfondir la réponse :

    Critique : {critique}

    Contexte : {context}

    Réponse initiale : {initial_response}

    Générez une liste de 3 à 5 nouvelles questions pertinentes, en vous concentrant sur les aspects suivants :
    1. Les points faibles ou manquants dans la réponse initiale.
    2. Les aspects du contexte qui n'ont pas été suffisamment abordés.
    3. Les opportunités d'approfondir ou de clarifier des éléments spécifiques.
    """

    response = query_llm(prompt)
    return extract_key_points(response)