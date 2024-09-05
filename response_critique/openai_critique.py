#response_critique/openai_critique.py

from openai import OpenAI
from typing import List, Dict
import os
from config.config import OPENAI_API_KEY


# Assurez-vous que votre clé API OpenAI est définie dans les variables d'environnement
client = OpenAI(api_key=OPENAI_API_KEY)


def generate_critique(question: str, answer: str, context: str, expert_analysis: str) -> str:
    prompt = f"""
    En tant qu'expert en analyse de demandes de subvention, examinez attentivement la réponse suivante à la question de subvention.

    Question : {question}
    Réponse : {answer}
    Contexte de la subvention : {context}
    Analyse d'expert : {expert_analysis}

    Veuillez fournir une critique constructive de la réponse en considérant les points suivants :
    1. Pertinence : La réponse répond-elle directement à la question posée ?
    2. Exhaustivité : Tous les aspects importants de la question sont-ils abordés ?
    3. Clarté : La réponse est-elle claire et bien structurée ?
    4. Alignement : La réponse est-elle en accord avec les objectifs et les critères de la subvention ?
    5. Points forts : Quels sont les points forts de la réponse ?
    6. Axes d'amélioration : Quels aspects pourraient être améliorés ?

    Veuillez structurer votre critique comme suit :

    Analyse :
    [Votre analyse détaillée ici]

    Points forts :
    - [Point fort 1]
    - [Point fort 2]
    - [Point fort 3]

    Axes d'amélioration :
    - [Suggestion d'amélioration 1]
    - [Suggestion d'amélioration 2]
    - [Suggestion d'amélioration 3]

    Assurez-vous que votre critique soit constructive, spécifique et actionnable.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Vous êtes un expert en analyse de demandes de subvention."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=10000,
        temperature=0
    )

    return response.choices[0].message.content


def critique_responses(questions: List[str], answers: Dict[str, str], context: str, expert_analysis: str,
                       project_name: str) -> Dict[str, str]:
    critiques = {}
    for question in questions:
        answer = answers.get(question, "")
        critique = generate_critique(question, answer, context, expert_analysis)
        critiques[question] = critique
    return critiques