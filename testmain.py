# Importations nécessaires
import os
from dotenv import load_dotenv

# Chargement des variables d'environnement depuis le fichier .env
load_dotenv()

# Récupération des clés API depuis les variables d'environnement
MISTRALAI_API_KEY = os.getenv('MISTRALAI_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
COHERE_API_KEY = os.getenv('COHERE_API_KEY')
LLAMA_CLOUD_API_KEY = os.getenv('LLAMA_CLOUD_API_KEY')

# Vérification que les clés API sont bien définies
if not all([MISTRALAI_API_KEY, OPENAI_API_KEY, COHERE_API_KEY, LLAMA_CLOUD_API_KEY]):
    raise ValueError("Toutes les clés API nécessaires ne sont pas définies dans le fichier .env")

# Configuration des clients et modèles avec les clés API sécurisées
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from llama_index.llms.mistralai import MistralAI

modelmai = "mistral-large-latest"
modelgpt = "gpt-4o-mini"
client = MistralClient(api_key=MISTRALAI_API_KEY)
llm = MistralAI(model=modelmai, api_key=MISTRALAI_API_KEY, temperature=0, random_seed=42, safe_mode=True)


def get_completion(prompt, model=modelmai):
    messages = [
        ChatMessage(role="user", content=prompt)
    ]

    # No streaming
    chat_response = client.chat(
        model=model,
        messages=messages,
    )
    return chat_response.choices[0].message.content


# Configuration de Cohere
from llama_index.postprocessor.cohere_rerank import CohereRerank
cohere_rerank = CohereRerank(api_key=COHERE_API_KEY, top_n=2)

# Configuration des embeddings
from llama_index.embeddings.cohere import CohereEmbedding
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import Settings


def cohere_embedding(
        model_name: str, input_type: str, embedding_type: str
) -> CohereEmbedding:
    return CohereEmbedding(
        cohere_api_key=os.environ["COHERE_API_KEY"],
        model_name=model_name,
        input_type=input_type,
        embedding_type=embedding_type,
    )


# Configuration des modèles d'embeddings et de langage
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import VectorStoreIndex
from llama_index.core import Settings

embed_model = OpenAIEmbedding(model="text-embedding-3-small")
Settings.llm = llm
Settings.embed_model = cohere_embedding("embed-multilingual-v3.0", "search_document", "float")

# Traitement du document de subvention
from llama_parse import LlamaParse

doc_subv = LlamaParse(result_type="markdown").load_data('files/Dossier-de-candidature-CCEIR-2024.docx')

from llama_index.core.node_parser import MarkdownElementNodeParser

node_parser = MarkdownElementNodeParser(llm=OpenAI(model=modelgpt), num_workers=8)

nodesubv = node_parser.get_nodes_from_documents(doc_subv)
base_nodessubv, objectsubv = node_parser.get_nodes_and_objects(nodesubv)
recursive_index_subv = VectorStoreIndex(nodes=base_nodessubv + objectsubv)

from llama_index.postprocessor.flag_embedding_reranker import FlagEmbeddingReranker

reranker = FlagEmbeddingReranker(
    top_n=5,
    model="BAAI/bge-reranker-large",
)

recursive_query_engine = recursive_index_subv.as_query_engine(
    similarity_top_k=15,
    node_postprocessors=[cohere_rerank],
    verbose=True
)

print(len(nodesubv))


# Extraction des questions du document de subvention
query = f""" 
Quelles sont les questions posées dans le dossier de subvention? 
Fais de ton mieux pour identifier toutes les questions posées hors porteur du projet. 
Ta sortie est une liste de question uniquement. Pas d'autres explications de texte. 
Le format est "numéro de question.question"
        """

list_q_subv = recursive_query_engine.query(query)

# Génération d'un résumé des questions
sumr_list_q_subv = get_completion(f""" 
Voici la liste de questions {list_q_subv} du dossier de subvention.
A partir de cette liste, génère uniquement 4 questions qui résument les grands sujets de la subvention la liste de questions hors porteur du projet.
Si dans cette liste aucune question n'est proche de la question suivante "Résume en une phrase  du projet ou de la solution proposé dans le document?". ajoute cette question à la liste de 4 en haut de liste.
Ta sortie correspond au modèle suivant: numéro de question.question
N'ajoute aucun autre texte que les questions. 
""")

doc_user = LlamaParse(result_type="markdown").load_data('files/FOLDR - Small Specifications.pdf')


nodespec = node_parser.get_nodes_from_documents(doc_user)
base_nodespec, objectspec = node_parser.get_nodes_and_objects(nodespec)
recursive_index_spec = VectorStoreIndex(nodes=base_nodespec + objectspec)

recursive_query_engine = recursive_index_spec.as_query_engine(
    similarity_top_k=15,
    node_postprocessors=[cohere_rerank],
    verbose=True
)


# Dictionnaires pour stocker les réponses
sumr_responses = {}
subv_responses = {}

import re


def extract_question_text(question):
    return question.split('. ', 1)[1].strip() if '. ' in question else question.strip()


# Fonction pour traiter chaque question et stocker les réponses au format Markdown
def process_questions(questions, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for idx, question in enumerate(questions, start=1):
        question_text = extract_question_text(question)
        response = recursive_query_engine.query(question_text)
        result = f"### Question\n\n{question_text}\n\n### Réponse trouvée dans le document\n\n{response}"

        output_file = os.path.join(output_dir, f"response_{idx}.md")

        with open(output_file, 'w') as file:
            file.write(result)


# Convertir la chaîne sumr_list_q_subv en liste de questions
sumr_list_q_subv_lines = sumr_list_q_subv.strip().split('\n')

# Répertoires de sortie
sumr_output_dir = "output/sumr_responses"
subv_output_dir = "subv_responses"

# Traiter les questions et stocker les réponses
process_questions(sumr_list_q_subv_lines, sumr_output_dir)

print("Les réponses ont été stockées dans les répertoires respectifs.")
