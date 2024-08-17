import os

def generate_answers(questions, query_engine, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for idx, question in enumerate(questions, start=1):
        question_text = question.split('. ', 1)[1].strip() if '. ' in question else question.strip()
        response = query_engine.query(question_text)
        result = f"### Question\n\n{question_text}\n\n### Réponse trouvée dans le document\n\n{response}"

        output_file = os.path.join(output_dir, f"response_{idx}.md")
        with open(output_file, 'w') as file:
            file.write(result)