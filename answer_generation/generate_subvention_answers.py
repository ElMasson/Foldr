import os


def generate_subvention_answers(questions, query_engine, output_dir, update_progress):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    responses = {}
    total_questions = len(questions)

    for idx, question in enumerate(questions, start=1):
        progress = min(70 + (idx / total_questions) * 30, 100)
        update_progress(progress, f"Traitement de la question {idx}/{total_questions}")

        response = query_engine.query(question)
        responses[question] = response.response if hasattr(response, 'response') else str(response)

        output_file = os.path.join(output_dir, f"subv_response_{idx}.md")
        with open(output_file, 'w') as file:
            file.write(f"### Question\n\n{question}\n\n### Réponse\n\n{responses[question]}")

    return responses