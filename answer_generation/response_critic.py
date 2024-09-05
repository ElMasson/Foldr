from crewai import Agent, Task, Crew
from langchain.chat_models import ChatOpenAI
from config.config import OPENAI_API_KEY


class ResponseCritic:
    def __init__(self, context, expert_analysis):
        self.context = context
        self.expert_analysis = expert_analysis
        self.llm = ChatOpenAI(model_name="gpt-4o-mini", openai_api_key=OPENAI_API_KEY)

    def critique_response(self, question, response):
        context_analyst = Agent(
            role='Analyste de Contexte',
            goal='Analyser la pertinence de la réponse par rapport au contexte de la subvention',
            backstory="Expert en analyse de contexte pour les demandes de subvention",
            allow_delegation=False,
            llm=self.llm
        )

        expert_critic = Agent(
            role='Critique Expert',
            goal='Évaluer la qualité et la pertinence de la réponse selon l\'analyse d\'expert',
            backstory="Expert en évaluation de demandes de subvention avec des années d'expérience",
            allow_delegation=False,
            llm=self.llm
        )

        improvement_advisor = Agent(
            role='Conseiller en Amélioration',
            goal='Proposer des axes d\'amélioration concrets pour la réponse',
            backstory="Consultant spécialisé dans l'optimisation des demandes de subvention",
            allow_delegation=False,
            llm=self.llm
        )

        context_analysis_task = Task(
            description=f"Analyser la pertinence de la réponse suivante par rapport au contexte de la subvention:\n\nQuestion: {question}\n\nRéponse: {response}\n\nContexte: {self.context}",
            agent=context_analyst
        )

        expert_critique_task = Task(
            description=f"Évaluer la qualité et la pertinence de la réponse suivante selon l'analyse d'expert:\n\nQuestion: {question}\n\nRéponse: {response}\n\nAnalyse d'expert: {self.expert_analysis}",
            agent=expert_critic
        )

        improvement_task = Task(
            description="Proposer des axes d'amélioration concrets pour la réponse en vous basant sur les analyses précédentes.",
            agent=improvement_advisor
        )

        crew = Crew(
            agents=[context_analyst, expert_critic, improvement_advisor],
            tasks=[context_analysis_task, expert_critique_task, improvement_task],
            verbose=True
        )

        result = crew.kickoff()
        return self.summarize_critique(result)

    def summarize_critique(self, crew_result):
        summary_prompt = f"""
        Résumez la critique de la réponse en un paragraphe concis, incluant :
        1. La pertinence par rapport au contexte
        2. La qualité selon l'analyse d'expert
        3. Les principaux axes d'amélioration proposés

        Critique complète :
        {crew_result}

        Résumé de la critique :
        """
        summary = self.llm.predict(summary_prompt)
        return summary