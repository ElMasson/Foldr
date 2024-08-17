from llama_index.llms.openai import OpenAI
from .config import OPENAI_API_KEY
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_questions(query_engine, model):
    logger.info("Début de l'extraction des questions")

    query = """
    Analyse en profondeur le document de subvention et identifie toutes les questions explicites et implicites posées.
    Inclus également les points clés qui nécessitent une réponse, même s'ils ne sont pas formulés sous forme de question.
    Organise ces questions et points clés par sections du document.
    Format de sortie :
    Section: [Nom de la section]
    1. [Question/Point clé 1]
    2. [Question/Point clé 2]
    ...

    Section: [Nom de la section suivante]
    1. [Question/Point clé 1]
    2. [Question/Point clé 2]
    ...
    """

    response = query_engine.query(query)
    logger.info(f"Questions extraites : {response}")

    return response


def summarize_questions(questions):
    llm = OpenAI(model="gpt-4o-mini", api_key=OPENAI_API_KEY)
    logger.info("Début de la summarization des questions")

    try:
        questions_text = "\n".join(questions)
        prompt = f"""
        Voici la liste de questions et points clés extraits du dossier de subvention :
        {questions_text}

        À partir de cette liste, génère 5 questions principales qui résument les grands thèmes de la subvention.
        Ces questions doivent être plus générales et englobantes que les questions spécifiques listées.
        Assure-toi que ces questions couvrent les aspects les plus importants du projet et de la demande de subvention.

        Format de sortie :
        1. [Question principale 1]
        2. [Question principale 2]
        3. [Question principale 3]
        4. [Question principale 4]
        5. [Question principale 5]

        N'ajoute aucun autre texte que les questions numérotées.
        """

        logger.info("Envoi de la requête à l'API")
        response = llm.complete(prompt)
        logger.info("Réponse reçue de l'API")

        summarized_questions = response.text.strip().split("\n")
        logger.info(f"Questions résumées : {summarized_questions}")

        return summarized_questions

    except Exception as e:
        logger.error(f"Erreur lors de la summarization des questions : {str(e)}")
        raise


def test_question_extraction(query_engine):
    questions = extract_questions(query_engine, "gpt-4o-mini")
    logger.info("Questions extraites:")
    logger.info(questions)

    summary = summarize_questions(questions.response.split('\n'))
    logger.info("Résumé des questions:")
    logger.info(summary)

    return questions, summary