from openai import OpenAI
from .config import OPENAI_API_KEY

class ResponseCritic:
    def __init__(self, context, expert_analysis):
        self.context = context
        self.expert_analysis = expert_analysis
        self.client = OpenAI(api_key=OPENAI_API_KEY)

    def _generate_response(self, prompt):
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    def critique_response(self, question, response):
        context_analysis_prompt = f"""
        Analysez la pertinence de la réponse suivante par rapport au contexte de la subvention:

        Question: {question}
        Réponse: {response}
        Contexte: {self.context}

        Analyse de pertinence:
        """
        context_analysis = self._generate_response(context_analysis_prompt)

        expert_critique_prompt = f"""
        Évaluez la qualité et la pertinence de la réponse suivante selon l'analyse d'expert:

        Question: {question}
        Réponse: {response}
        Analyse d'expert: {self.expert_analysis}

        Critique expert:
        """
        expert_critique = self._generate_response(expert_critique_prompt)

        improvement_prompt = f"""
        Proposez des axes d'amélioration concrets pour la réponse en vous basant sur les analyses précédentes:

        Analyse de pertinence: {context_analysis}
        Critique expert: {expert_critique}

        Axes d'amélioration:
        """
        improvement = self._generate_response(improvement_prompt)

        return self.summarize_critique(context_analysis, expert_critique, improvement)

    def summarize_critique(self, context_analysis, expert_critique, improvement):
        summary_prompt = f"""
        Résumez la critique de la réponse en un paragraphe concis, incluant :
        1. La pertinence par rapport au contexte
        2. La qualité selon l'analyse d'expert
        3. Les principaux axes d'amélioration proposés

        Analyse de pertinence:
        {context_analysis}

        Critique expert:
        {expert_critique}

        Axes d'amélioration:
        {improvement}

        Résumé de la critique:
        """
        return self._generate_response(summary_prompt)