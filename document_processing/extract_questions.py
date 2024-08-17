from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from config.config import MISTRALAI_API_KEY

def extract_questions(query_engine, model):
    query = """
    Quelles sont les questions posées dans le dossier de subvention? 
    Fais de ton mieux pour identifier toutes les questions posées hors porteur du projet. 
    Ta sortie est une liste de question uniquement. Pas d'autres explications de texte. 
    Le format est "numéro de question.question"
    """
    return query_engine.query(query)

def summarize_questions(questions, model):
    client = MistralClient(api_key=MISTRALAI_API_KEY)
    prompt = f"""
    Voici la liste de questions {questions} du dossier de subvention.
    A partir de cette liste, génère uniquement 4 questions qui résument les grands sujets de la subvention la liste de questions hors porteur du projet.
    Si dans cette liste aucune question n'est proche de la question suivante "Résume en une phrase du projet ou de la solution proposé dans le document?". ajoute cette question à la liste de 4 en haut de liste.
    Ta sortie correspond au modèle suivant: numéro de question.question
    N'ajoute aucun autre texte que les questions.
    """
    response = client.chat(model=model, messages=[ChatMessage(role="user", content=prompt)])
    return response.choices[0].message.content