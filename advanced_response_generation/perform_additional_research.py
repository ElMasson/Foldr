#advanced_response_generation/perform_additional_research.py

from typing import List, Dict
from web_search.search_google import search_google
from web_search.process_search_results import process_search_results
from document_processing.process_document import process_document
from .utils import query_llm, merge_responses

def perform_additional_research(questions: List[str], context: str, user_document_path: str) -> Dict[str, str]:
    """
    Effectue des recherches supplémentaires pour chaque nouvelle question identifiée.

    Args:
        questions (List[str]): Liste des nouvelles questions à rechercher.
        context (str): Le contexte de la subvention.
        user_document_path (str): Chemin vers le document utilisateur.

    Returns:
        Dict[str, str]: Un dictionnaire avec les questions comme clés et les réponses comme valeurs.
    """
    research_results = {}

    # Traitement du document utilisateur
    user_index = process_document(user_document_path, "gpt-4o-mini")
    user_query_engine = user_index.as_query_engine()

    for question in questions:
        # Recherche dans le document utilisateur
        user_doc_response = user_query_engine.query(question)

        # Recherche sur Internet
        search_query = f"{question} {context}"
        search_results = search_google(search_query)
        internet_results = process_search_results(search_results, context)

        # Fusion des résultats
        prompt = f"""
        Combinez les informations suivantes pour fournir une réponse concise et pertinente à la question :

        Question : {question}

        Informations du document utilisateur : {user_doc_response.response}

        Résultats de recherche Internet : {internet_results}

        Contexte de la subvention : {context}

        Fournissez une réponse synthétisée qui intègre les informations les plus pertinentes des deux sources.
        """

        research_results[question] = query_llm(prompt)

    return research_results