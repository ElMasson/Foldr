#answer_generation/generate_answers.py

from typing import List, Dict

def generate_answers(questions: List[str], query_engine, model: str = "gpt-4o-mini") -> Dict[str, str]:
    answers = {}
    for question in questions:
        response = query_engine.query(question)
        answers[question] = response.response if hasattr(response, 'response') else str(response)
    return answers


# Note: La fonction ci-dessous n'est plus utilisée directement, mais peut être conservée pour référence
def save_answers(project_name: str, answers: Dict[str, str], output_dir: str):
    import os
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for idx, (question, answer) in enumerate(answers.items(), start=1):
        output_file = os.path.join(output_dir, f"response_{idx}.md")
        with open(output_file, 'w') as file:
            file.write(f"### Question\n\n{question}\n\n### Réponse\n\n{answer}")