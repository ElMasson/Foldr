from crewai import Crew, Agent, Task
from typing import List, Dict
import os
from config.config import OPENAI_API_KEY

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

def create_critique_expert():
    return Agent(
        role='Critique Expert',
        goal='Analyser et critiquer la réponse à la question de subvention',
        backstory="Vous êtes un expert en analyse de demandes de subvention avec des années d'expérience dans l'évaluation de propositions.",
        verbose=True
    )

def create_improvement_advisor():
    return Agent(
        role='Conseiller en Amélioration',
        goal='Proposer des axes d amélioration concrets pour la réponse',
        backstory="Vous êtes un consultant spécialisé dans l'optimisation des demandes de subvention, avec une connaissance approfondie des attentes des comités d'évaluation.",
        verbose=True
    )


def generate_critique(question: str, answer: str, context: str, expert_analysis: str) -> str:
    critique_expert = create_critique_expert()
    improvement_advisor = create_improvement_advisor()

    critique_task = Task(
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
        agent=critique_expert,
        expected_output="Une critique détaillée de la réponse à la question de subvention"
    )

    improvement_task = Task(
        description="""
        Sur la base de l'analyse précédente, proposez des axes d'amélioration concrets pour la réponse. 
        Soyez spécifique et actionnable dans vos suggestions.
        """,
        agent=improvement_advisor,
        expected_output="Une liste d'au moins trois recommandations détaillées pour améliorer la réponse"
    )

    crew = Crew(
        agents=[critique_expert, improvement_advisor],
        tasks=[critique_task, improvement_task],
        verbose=True
    )

    result = crew.kickoff()
    return result


def critique_responses(questions: List[str], answers: Dict[str, str], context: str, expert_analysis: str,
                       project_name: str) -> Dict[str, str]:
    critiques = {}
    for question in questions:
        answer = answers.get(question, "")
        critique = generate_critique(question, answer, context, expert_analysis)
        critiques[question] = critique
    return critiques