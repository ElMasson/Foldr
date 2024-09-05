#document_processing/extract_questions.py

from openai import OpenAI
from config.config import OPENAI_API_KEY

# Initialiser le client OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)


def extract_questions(query_engine, model="gpt-4o-mini"):
    query = """
    Quelles sont les questions posées dans le dossier de subvention? 
    Fais de ton mieux pour identifier toutes les questions posées hors porteur du projet. 
    Ta sortie est une liste de question uniquement. Pas d'autres explications de texte. 
    Le format est "numéro de question.question"
    """
    response = query_engine.query(query)

    # Si la réponse est un objet avec un attribut 'response', retournez cet attribut
    if hasattr(response, 'response'):
        return response.response
    # Sinon, si c'est déjà une chaîne de caractères, retournez-la directement
    elif isinstance(response, str):
        return response
    # Dans tous les autres cas, convertissez la réponse en chaîne de caractères
    else:
        return str(response)


def summarize_questions(questions, internet_context, model="gpt-4o-mini"):
    prompt = f"""
    Contexte de la subvention obtenu à partir de la recherche Internet :
    {internet_context}

    Voici la liste des questions identifiées dans le dossier de subvention :
    {questions}

    En tenant compte du contexte de la subvention fourni ci-dessus, identifiez les 4 questions les plus pertinentes et importantes parmi celles listées. Ces questions doivent être celles qui auront le plus grand impact sur l'évaluation de la demande de subvention, en fonction des critères et des priorités mentionnés dans le contexte.

    Si aucune des questions listées ne couvre l'aspect suivant, ajoutez-la comme l'une des 4 questions : "Résumez en une phrase le projet ou la solution proposée dans le document."

    Présentez les 4 questions sélectionnées ou créées selon le format suivant :
    1. [Question 1]
    2. [Question 2]
    3. [Question 3]
    4. [Question 4]

    N'ajoutez aucun autre texte ou explication en dehors de ces 4 questions numérotées.
    """

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system",
             "content": "Vous êtes un expert en analyse de dossiers de subvention, capable d'identifier les questions les plus cruciales en fonction du contexte fourni."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=10000,
        temperature=0
    )

    return response.choices[0].message.content


def use_gpt4o_mini(prompt, max_tokens=10000, temperature=0):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Vous êtes un assistant expert en analyse de dossiers de subvention."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=max_tokens,
        temperature=temperature
    )
    return response.choices[0].message.content