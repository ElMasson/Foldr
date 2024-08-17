import os
from typing import List, Dict
from llama_index.core import VectorStoreIndex
from llama_index.llms.openai import OpenAI
from .config import OPENAI_API_KEY

class AdvancedAnswerGenerator:
    def __init__(self, query_engine, llm_model="gpt-4"):
        self.query_engine = query_engine
        self.llm = OpenAI(model=llm_model, api_key=OPENAI_API_KEY)

    def generate_subquestions(self, main_question: str) -> List[str]:
        prompt = f"""
        Based on the following main question, generate 3-5 detailed subquestions that will help provide a comprehensive answer:

        Main question: {main_question}

        Subquestions:
        1.
        """
        response = self.llm.complete(prompt)
        subquestions = [q.strip() for q in response.text.split('\n') if q.strip()]
        return subquestions

    def get_detailed_answers(self, questions: List[str]) -> Dict[str, str]:
        answers = {}
        for question in questions:
            response = self.query_engine.query(question)
            answers[question] = response.response if hasattr(response, 'response') else str(response)
        return answers

    def synthesize_final_answer(self, main_question: str, detailed_answers: Dict[str, str]) -> str:
        context = "\n\n".join([f"Question: {q}\nAnswer: {a}" for q, a in detailed_answers.items()])
        prompt = f"""
        Based on the following detailed answers to subquestions, provide a comprehensive and cohesive answer to the main question:

        Main question: {main_question}

        Detailed information:
        {context}

        Synthesized answer:
        """
        response = self.llm.complete(prompt)
        return response.text

    def improve_answer(self, question: str, initial_answer: str) -> str:
        prompt = f"""
        Please improve the following answer to make it more comprehensive, well-structured, and persuasive for a grant application:

        Question: {question}

        Initial Answer: {initial_answer}

        Improved Answer:
        """
        response = self.llm.complete(prompt)
        return response.text

    def generate_advanced_answer(self, question: str) -> str:
        subquestions = self.generate_subquestions(question)
        detailed_answers = self.get_detailed_answers([question] + subquestions)
        initial_answer = self.synthesize_final_answer(question, detailed_answers)
        improved_answer = self.improve_answer(question, initial_answer)
        return improved_answer

def generate_advanced_answers(questions: List[str], query_engine: VectorStoreIndex, output_dir: str, update_progress):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    advanced_generator = AdvancedAnswerGenerator(query_engine)
    responses = {}
    total_questions = len(questions)

    for idx, question in enumerate(questions, start=1):
        if question.strip():
            progress = min(70 + (idx / total_questions) * 30, 100)
            update_progress(progress, f"Traitement approfondi de la question {idx}/{total_questions}")

            advanced_answer = advanced_generator.generate_advanced_answer(question)
            responses[question] = advanced_answer

            output_file = os.path.join(output_dir, f"advanced_response_{idx}.md")
            with open(output_file, 'w') as file:
                file.write(f"### Question\n\n{question}\n\n### Réponse détaillée\n\n{advanced_answer}")

    return responses

def generate_answers(questions, query_engine, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for idx, question in enumerate(questions, start=1):
        question_text = question.split('. ', 1)[1].strip() if '. ' in question else question.strip()
        if question_text:
            response = query_engine.query(question_text)
            result = f"### Question\n\n{question_text}\n\n### Réponse trouvée dans le document\n\n{response}"

            output_file = os.path.join(output_dir, f"response_{idx}.md")
            with open(output_file, 'w') as file:
                file.write(result)

def generate_subvention_answers(questions, query_engine, output_dir, update_progress):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    responses = {}
    total_questions = len(questions)

    for idx, question in enumerate(questions, start=1):
        if question.strip():
            progress = min(70 + (idx / total_questions) * 30, 100)
            update_progress(progress, f"Traitement de la question {idx}/{total_questions}")

            response = query_engine.query(question)
            responses[question] = response.response if hasattr(response, 'response') else str(response)

            output_file = os.path.join(output_dir, f"subv_response_{idx}.md")
            with open(output_file, 'w') as file:
                file.write(f"### Question\n\n{question}\n\n### Réponse\n\n{responses[question]}")

    return responses