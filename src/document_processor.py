from llama_parse import LlamaParse
from llama_index.core.node_parser import MarkdownElementNodeParser
from llama_index.core import VectorStoreIndex, Document
from llama_index.llms.openai import OpenAI
from .config import OPENAI_API_KEY
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def process_document(file_path, model_gpt):
    logger.info(f"Début du traitement du document : {file_path}")

    try:
        doc = LlamaParse(result_type="markdown").load_data(file_path)
        logger.info(f"Document chargé avec succès. Nombre de pages : {len(doc)}")

        llm = OpenAI(model=model_gpt, api_key=OPENAI_API_KEY)
        node_parser = MarkdownElementNodeParser(llm=llm, num_workers=8)

        nodes = node_parser.get_nodes_from_documents(doc)
        logger.info(f"Nombre de nœuds extraits : {len(nodes)}")

        base_nodes, objects = node_parser.get_nodes_and_objects(nodes)
        logger.info(f"Nombre de nœuds de base : {len(base_nodes)}, Nombre d'objets : {len(objects)}")

        # Ajout d'un nœud supplémentaire contenant tout le texte du document
        full_text = "\n".join([node.text for node in base_nodes])
        full_text_node = Document(text=full_text, extra_info={"source": "full_document"})

        index = VectorStoreIndex(nodes=base_nodes + objects + [full_text_node])
        logger.info("Index vectoriel créé avec succès")

        return index
    except Exception as e:
        logger.error(f"Erreur lors du traitement du document : {str(e)}")
        raise


def test_document_processing(file_path, model_gpt):
    index = process_document(file_path, model_gpt)
    query_engine = index.as_query_engine()

    test_queries = [
        "Quel est le sujet principal du document?",
        "Quelles sont les principales sections du document?",
        "Pouvez-vous résumer le contenu du document en quelques phrases?"
    ]

    for query in test_queries:
        response = query_engine.query(query)
        logger.info(f"Query: {query}")
        logger.info(f"Response: {response}")
        logger.info("---")

    return index