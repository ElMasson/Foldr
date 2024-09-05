#web_search/process_search_results.py

from llama_index.llms.openai import OpenAI
from config.config import OPENAI_API_KEY


def process_search_results(results, context):
    llm = OpenAI(model="gpt-4o-mini", api_key=OPENAI_API_KEY)

    combined_text = "\n".join([f"Title: {item['title']}\nSnippet: {item['snippet']}" for item in results])

    prompt = f"""
    Contexte: {context}

    Voici des résultats de recherche sur ce concours ou cette subvention:

    {combined_text}

    À partir de ces informations, génère un résumé concis (environ 200 mots) qui inclut :
    1. Le contexte général du concours ou de la subvention
    2. Les objectifs principaux
    3. Les critères d'éligibilité importants
    4. Toute autre information pertinente pour aider à améliorer une demande de subvention

    Présente ces informations de manière structurée et facile à lire.
    """

    response = llm.complete(prompt)
    return response.text


def expert_analysis(context_summary):
    llm = OpenAI(model="gpt-4o-mini", api_key=OPENAI_API_KEY)

    prompt = f"""
    En tant qu'expert en rédaction de demandes de subventions, analyse le résumé suivant et fournit une interprétation détaillée pour guider la rédaction de la réponse :

    {context_summary}

    Dans ton analyse, inclus les éléments suivants :
    1. Éléments clés : Identifie les points cruciaux à aborder dans la demande.
    2. Attentes du comité : Décris ce que le comité de sélection recherche probablement.
    3. Style de rédaction : Recommande un ton et un style appropriés pour la demande.
    4. Points à mettre en avant : Suggère les aspects du projet à souligner particulièrement.
    5. Pièges à éviter : Mentionne les erreurs courantes ou les points à ne pas négliger.
    6. Conseils de structuration : Propose une organisation logique pour la demande.

    Présente ton analyse de manière claire et actionnable pour guider efficacement la rédaction de la demande de subvention.
    """

    response = llm.complete(prompt)
    return response.text