import os
from typing import List, Dict
from crewai import Agent, Task


def create_critique_expert() -> Agent:
    """
    Crée et retourne un agent Crew AI expert en critique de demandes de subvention.

    :return: Un agent Crew AI
    """
    return Agent(
        role='Critique Expert',
        goal='Analyser et critiquer la réponse à la question de subvention',
        backstory="Vous êtes un expert en analyse de demandes de subvention avec des années d'expérience dans l'évaluation de propositions. Votre objectif est de fournir des critiques constructives et détaillées pour aider à améliorer les réponses.",
        verbose=True
    )


def create_improvement_advisor() -> Agent:
    """
    Crée et retourne un agent Crew AI conseiller en amélioration.

    :return: Un agent Crew AI
    """
    return Agent(
        role='Conseiller en Amélioration',
        goal='Proposer des axes d amélioration concrets pour la réponse',
    backstory = "Vous êtes un consultant spécialisé dans l'optimisation des demandes de subvention, avec une connaissance approfondie des attentes des comités d'évaluation. Votre rôle est de suggérer des améliorations spécifiques et actionnables.",
    verbose = True
    )


def create_critique_task(question: str, answer: str, context: str, expert_analysis: str) -> Task:
    """
    Crée une tâche de critique pour Crew AI.

    :param question: La question de la subvention
    :param answer: La réponse fournie
    :param context: Le contexte de la subvention
    :param expert_analysis: L'analyse d'expert préalable
    :return: Une tâche Crew AI
    """
    return Task(
        description=f"""
        Analysez la réponse suivante à la question de subvention: 
        Question: '{question}'
        Réponse: '{answer}'
        Contexte: '{context}'
        Analyse d'expert: '{expert_analysis}'

        Évaluez sa pertinence, sa clarté et son alignement avec les attentes probables du comité de subvention.
        Fournissez une critique détaillée incluant :
        1. Une analyse générale
        2. Les points forts de la réponse
        3. Les axes d'amélioration spécifiques
        """,
        agent=create_critique_expert()
    )


def create_improvement_task() -> Task:
    """
    Crée une tâche d'amélioration pour Crew AI.

    :return: Une tâche Crew AI
    """
    return Task(
        description="""
        Sur la base de l'analyse précédente, proposez des axes d'amélioration concrets pour la réponse. 
        Soyez spécifique et actionnable dans vos suggestions. 
        Fournissez au moins trois recommandations détaillées pour améliorer la réponse.
        """,
        agent=create_improvement_advisor()
    )


def save_critique(project_name: str, question: str, critique: str) -> None:
    """
    Sauvegarde la critique générée dans un fichier.

    :param project_name: Le nom du projet
    :param question: La question à laquelle la critique est associée
    :param critique: Le contenu de la critique
    """
    output_dir = f"output/{project_name}/critiques"
    os.makedirs(output_dir, exist_ok=True)

    safe_filename = "".join(c for c in question if c.isalnum() or c in (' ', '_')).rstrip()
    safe_filename = safe_filename[:50]

    file_path = os.path.join(output_dir, f"{safe_filename}.txt")

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(critique)


def load_critique(project_name: str, question: str) -> str:
    """
    Charge la critique sauvegardée pour une question donnée.

    :param project_name: Le nom du projet
    :param question: La question associée à la critique
    :return: Le contenu de la critique ou None si non trouvé
    """
    output_dir = f"output/{project_name}/critiques"

    safe_filename = "".join(c for c in question if c.isalnum() or c in (' ', '_')).rstrip()
    safe_filename = safe_filename[:50]

    file_path = os.path.join(output_dir, f"{safe_filename}.txt")

    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    return None


def generate_critique(question: str, answer: str, context: str, expert_analysis: str) -> str:
    """
    Génère une critique pour une réponse donnée en utilisant Crew AI.

    :param question: La question de la subvention
    :param answer: La réponse fournie
    :param context: Le contexte de la subvention
    :param expert_analysis: L'analyse d'expert préalable
    :return: La critique générée
    """
    from crewai import Crew

    critique_task = create_critique_task(question, answer, context, expert_analysis)
    improvement_task = create_improvement_task()

    crew = Crew(
        tasks=[critique_task, improvement_task],
        verbose=2
    )

    result = crew.kickoff()
    return result


def critique_responses(project_name: str, questions: List[str], answers: Dict[str, str], context: str,
                       expert_analysis: str) -> Dict[str, str]:
    """
    Génère des critiques pour un ensemble de réponses.

    :param project_name: Le nom du projet
    :param questions: Liste des questions
    :param answers: Dictionnaire des réponses (clé: question, valeur: réponse)
    :param context: Le contexte de la subvention
    :param expert_analysis: L'analyse d'expert préalable
    :return: Dictionnaire des critiques (clé: question, valeur: critique)
    """
    critiques = {}
    for question in questions:
        answer = answers.get(question, "")
        existing_critique = load_critique(project_name, question)
        if existing_critique:
            critiques[question] = existing_critique
        else:
            critique = generate_critique(question, answer, context, expert_analysis)
            save_critique(project_name, question, critique)
            critiques[question] = critique
    return critiques