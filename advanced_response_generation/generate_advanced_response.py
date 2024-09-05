#advanced_response_generation/generate_advanced_response.py

import os
from llama_index.core import (
    VectorStoreIndex,
    Document,
    ServiceContext,
    StorageContext,
    load_index_from_storage,
)
from llama_index.core.node_parser import HierarchicalNodeParser, get_leaf_nodes
from llama_index.core.retrievers import AutoMergingRetriever
from llama_index.core.indices.postprocessor import SentenceTransformerRerank
from llama_index.core.query_engine import RetrieverQueryEngine
from typing import Dict, List
from .identify_new_questions import identify_new_questions
from .perform_additional_research import perform_additional_research
from .compile_final_response import compile_final_response


def build_automerging_index(
        documents,
        llm,
        embed_model="local:BAAI/bge-small-en-v1.5",
        save_dir="merging_index",
        chunk_sizes=None,
):
    chunk_sizes = chunk_sizes or [2048, 512, 128]
    node_parser = HierarchicalNodeParser.from_defaults(chunk_sizes=chunk_sizes)
    nodes = node_parser.get_nodes_from_documents(documents)
    leaf_nodes = get_leaf_nodes(nodes)
    service_context = ServiceContext.from_defaults(
        llm=llm,
        embed_model=embed_model,
    )

    if not os.path.exists(save_dir):
        storage_context = StorageContext.from_defaults()
        storage_context.docstore.add_documents(nodes)
        automerging_index = VectorStoreIndex(
            leaf_nodes, storage_context=storage_context, service_context=service_context
        )
        automerging_index.storage_context.persist(persist_dir=save_dir)
    else:
        storage_context = StorageContext.from_defaults(persist_dir=save_dir)
        automerging_index = load_index_from_storage(
            storage_context, service_context=service_context
        )
    return automerging_index


def get_automerging_query_engine(
        automerging_index,
        similarity_top_k=12,
        rerank_top_n=6,
):
    base_retriever = automerging_index.as_retriever(similarity_top_k=similarity_top_k)
    retriever = AutoMergingRetriever(
        base_retriever, automerging_index.storage_context, verbose=True
    )
    rerank = SentenceTransformerRerank(
        top_n=rerank_top_n, model="BAAI/bge-reranker-base"
    )
    auto_merging_engine = RetrieverQueryEngine.from_args(
        retriever, node_postprocessors=[rerank]
    )
    return auto_merging_engine


def generate_advanced_response(question: str, critique: str, context: str, initial_response: str,
                               user_document_path: str) -> Dict[str, str]:
    """
    Génère une réponse avancée en utilisant un processus enrichi d'analyse et de recherche.
    """
    new_questions = identify_new_questions(critique, context, initial_response)
    additional_research = perform_additional_research(new_questions, context, user_document_path)
    final_response = compile_final_response(question, critique, context, initial_response, additional_research)

    structured_response = structure_response(final_response)

    result = {
        "text": structured_response,
        "new_questions": new_questions,
        "additional_research": additional_research
    }

    return result


def structure_response(response: str) -> str:
    """
    Évalue la réponse et la structure avec des éléments tabulaires si nécessaire.
    """
    # Identifier les parties qui pourraient bénéficier d'une structure tabulaire
    sections = response.split('\n\n')
    structured_sections = []

    for section in sections:
        if ':' in section and '\n' in section:
            # Potentiel pour une structure tabulaire
            lines = section.split('\n')
            if all(':' in line for line in lines[1:]):
                # Convertir en tableau
                headers = ["Élément", "Description"]
                data = [[line.split(':', 1)[0].strip(), line.split(':', 1)[1].strip()] for line in lines[1:]]
                table = create_table_markdown(headers, data)
                structured_sections.append(lines[0] + '\n\n' + table)
            else:
                structured_sections.append(section)
        else:
            structured_sections.append(section)

    return '\n\n'.join(structured_sections)


def create_table_markdown(headers: List[str], data: List[List[str]]) -> str:
    """
    Crée une représentation markdown d'un tableau.
    """
    table = "| " + " | ".join(headers) + " |\n"
    table += "| " + " | ".join(["---" for _ in headers]) + " |\n"
    for row in data:
        table += "| " + " | ".join(row) + " |\n"
    return table