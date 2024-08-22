from llama_index.core import VectorStoreIndex
from llama_index.core.node_parser import MarkdownElementNodeParser
from llama_index.llms.openai import OpenAI
from llama_parse import LlamaParse
from config.config import OPENAI_API_KEY

def process_document(file_path: str, model: str = "gpt-4o-mini") -> VectorStoreIndex:
    doc = LlamaParse(result_type="markdown").load_data(file_path)
    node_parser = MarkdownElementNodeParser(llm=OpenAI(model=model, api_key=OPENAI_API_KEY), num_workers=8)
    nodes = node_parser.get_nodes_from_documents(doc)
    base_nodes, objects = node_parser.get_nodes_and_objects(nodes)
    return VectorStoreIndex(nodes=base_nodes + objects)