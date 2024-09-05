import nest_asyncio
import os


# Configuration de l'API OpenAI
os.environ["OPENAI_API_KEY"] = "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"  # Remplacez par votre clé API

input_file = "files/user_YC Combinator DUKE application.pdf"

nest_asyncio.apply()

from llama_index.core import SimpleDirectoryReader

# load documents
documents = SimpleDirectoryReader(input_files=[input_file]).load_data()

from llama_index.core.node_parser import SentenceSplitter

splitter = SentenceSplitter(chunk_size=1024)
nodes = splitter.get_nodes_from_documents(documents)

from llama_index.core import Settings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding

Settings.llm = OpenAI(model="gpt-4o")
Settings.embed_model = OpenAIEmbedding(model="text-embedding-ada-002")

from llama_index.core import SummaryIndex, VectorStoreIndex

summary_index = SummaryIndex(nodes)
vector_index = VectorStoreIndex(nodes)

summary_query_engine = summary_index.as_query_engine(
    response_mode="tree_summarize",
    use_async=True,
)
vector_query_engine = vector_index.as_query_engine()

from llama_index.core.tools import QueryEngineTool


summary_tool = QueryEngineTool.from_defaults(
    query_engine=summary_query_engine,
    description=(
        "Useful for summarization questions related to DUKE"
    ),
)

vector_tool = QueryEngineTool.from_defaults(
    query_engine=vector_query_engine,
    description=(
        "Useful for retrieving specific context from the DUKE paper."
    ),
)

from llama_index.core.query_engine.router_query_engine import RouterQueryEngine
from llama_index.core.selectors import LLMSingleSelector


query_engine = RouterQueryEngine(
    selector=LLMSingleSelector.from_defaults(),
    query_engine_tools=[
        summary_tool,
        vector_tool,
    ],
    verbose=True
)

response = query_engine.query("What is the summary of the document?")
print(str(response))

print(len(response.source_nodes))

response = query_engine.query(
    "What are all the question asked in the document?"
)
print(str(response))


def get_router_query_engine(file_path: str, llm=None, embed_model=None):
    """Get router query engine."""
    llm = llm or OpenAI(model="gpt-4o-mini")
    embed_model = embed_model or OpenAIEmbedding(model="text-embedding-ada-002")

    # load documents
    documents = SimpleDirectoryReader(input_files=[file_path]).load_data()

    splitter = SentenceSplitter(chunk_size=1024)
    nodes = splitter.get_nodes_from_documents(documents)

    summary_index = SummaryIndex(nodes)
    vector_index = VectorStoreIndex(nodes, embed_model=embed_model)

    summary_query_engine = summary_index.as_query_engine(
        response_mode="tree_summarize",
        use_async=True,
        llm=llm
    )
    vector_query_engine = vector_index.as_query_engine(llm=llm)

    summary_tool = QueryEngineTool.from_defaults(
        query_engine=summary_query_engine,
        description=(
            "Useful for summarization questions related to DUKE"
        ),
    )

    vector_tool = QueryEngineTool.from_defaults(
        query_engine=vector_query_engine,
        description=(
            "Useful for retrieving specific context from the DUKE paper."
        ),
    )

    query_engine = RouterQueryEngine(
        selector=LLMSingleSelector.from_defaults(),
        query_engine_tools=[
            summary_tool,
            vector_tool,
        ],
        verbose=True
    )
    return query_engine

query_engine = get_router_query_engine(input_file)

response = query_engine.query("Tell me about the founder of DUKE?")
print(str(response))

from llama_index.core import SimpleDirectoryReader
# load documents
documents = SimpleDirectoryReader(input_files=[input_file]).load_data()

from llama_index.core.node_parser import SentenceSplitter
splitter = SentenceSplitter(chunk_size=1024)
nodes = splitter.get_nodes_from_documents(documents)

print(nodes[0].get_content(metadata_mode="all"))

from llama_index.core import VectorStoreIndex

vector_index = VectorStoreIndex(nodes)
query_engine = vector_index.as_query_engine(similarity_top_k=2)


from llama_index.core.vector_stores import MetadataFilters

query_engine = vector_index.as_query_engine(
    similarity_top_k=2,
    filters=MetadataFilters.from_dicts(
        [
            {"key": "page_label", "value": "2"}
        ]
    )
)

response = query_engine.query(
    "What are some high-level results of DUKE?",
)

print(str(response))

for n in response.source_nodes:
    print(n.metadata)

from typing import List
from llama_index.core.vector_stores import FilterCondition

from llama_index.core.tools import FunctionTool

def vector_query(
        query: str,
        page_numbers: List[str]
) -> str:
    """Perform a vector search over an index.

    query (str): the string query to be embedded.
    page_numbers (List[str]): Filter by set of pages. Leave BLANK if we want to perform a vector search
        over all pages. Otherwise, filter by the set of specified pages.

    """

    metadata_dicts = [
        {"key": "page_label", "value": p} for p in page_numbers
    ]

    query_engine = vector_index.as_query_engine(
        similarity_top_k=2,
        filters=MetadataFilters.from_dicts(
            metadata_dicts,
            condition=FilterCondition.OR
        )
    )
    response = query_engine.query(query)
    return response


vector_query_tool = FunctionTool.from_defaults(
    name="vector_tool",
    fn=vector_query
)

llm = OpenAI(model="gpt-4o-mini", temperature=0)
response = llm.predict_and_call(
    [vector_query_tool],
    "What are the high-level results of DUKE AI as described on page 9?",
    verbose=True
)


for n in response.source_nodes:
    print(n.metadata)


from llama_index.core import SummaryIndex
from llama_index.core.tools import QueryEngineTool

summary_index = SummaryIndex(nodes)
summary_query_engine = summary_index.as_query_engine(
    response_mode="tree_summarize",
    use_async=True,
)
summary_tool = QueryEngineTool.from_defaults(
    name="summary_tool",
    query_engine=summary_query_engine,
    description=(
        "Useful if you want to get a summary of DUKE AI"
    ),
)

response = llm.predict_and_call(
    [vector_query_tool, summary_tool],
    "What are the DUKE AI comparisons with its competitors described on page 9?",
    verbose=True
)

for n in response.source_nodes:
    print(n.metadata)

# TODO: abstract all of this into a function that takes in a PDF file name

from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, SummaryIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.tools import FunctionTool, QueryEngineTool
from llama_index.core.vector_stores import MetadataFilters, FilterCondition
from typing import List, Optional


def get_doc_tools(
        file_path: str,
        name: str,
) -> str:
    """Get vector query and summary query tools from a document."""

    # load documents
    documents = SimpleDirectoryReader(input_files=[file_path]).load_data()
    splitter = SentenceSplitter(chunk_size=1024)
    nodes = splitter.get_nodes_from_documents(documents)
    vector_index = VectorStoreIndex(nodes)

    def vector_query(
            query: str,
            page_numbers: Optional[List[str]] = None
    ) -> str:
        """Use to answer questions over the DUKE paper.

        Useful if you have specific questions over the DUKE paper.
        Always leave page_numbers as None UNLESS there is a specific page you want to search for.

        Args:
            query (str): the string query to be embedded.
            page_numbers (Optional[List[str]]): Filter by set of pages. Leave as NONE
                if we want to perform a vector search
                over all pages. Otherwise, filter by the set of specified pages.

        """

        page_numbers = page_numbers or []
        metadata_dicts = [
            {"key": "page_label", "value": p} for p in page_numbers
        ]

        query_engine = vector_index.as_query_engine(
            similarity_top_k=2,
            filters=MetadataFilters.from_dicts(
                metadata_dicts,
                condition=FilterCondition.OR
            )
        )
        response = query_engine.query(query)
        return response

    vector_query_tool = FunctionTool.from_defaults(
        name=f"vector_tool_{name}",
        fn=vector_query
    )

    summary_index = SummaryIndex(nodes)
    summary_query_engine = summary_index.as_query_engine(
        response_mode="tree_summarize",
        use_async=True,
    )
    summary_tool = QueryEngineTool.from_defaults(
        name=f"summary_tool_{name}",
        query_engine=summary_query_engine,
        description=(
            "Use ONLY IF you want to get a holistic summary of DUKE. "
            "Do NOT use if you have specific questions over DUKE."
        ),
    )

    return vector_query_tool, summary_tool


vector_tool, summary_tool = get_doc_tools(input_file, "DUKE")

llm = OpenAI(model="gpt-4o-mini", temperature=0)

from llama_index.core.agent import FunctionCallingAgentWorker
from llama_index.core.agent import AgentRunner

agent_worker = FunctionCallingAgentWorker.from_tools(
    [vector_tool, summary_tool],
    llm=llm,
    verbose=True
)
agent = AgentRunner(agent_worker)

response = agent.query(
    "Tell me about the agent roles in DUKE, "
    "and then how they communicate with each other."
)


response = agent.chat(
    "Tell me about the AI  used."
)

agent_worker = FunctionCallingAgentWorker.from_tools(
    [vector_tool, summary_tool],
    llm=llm,
    verbose=True
)
agent = AgentRunner(agent_worker)

task = agent.create_task(
    "Tell me about the agent roles in DUKE, "
    "and then how they communicate with each other."
)

step_output = agent.run_step(task.task_id)

completed_steps = agent.get_completed_steps(task.task_id)
print(f"Num completed for task {task.task_id}: {len(completed_steps)}")
print(completed_steps[0].output.sources[0].raw_output)

upcoming_steps = agent.get_upcoming_steps(task.task_id)
print(f"Num upcoming steps for task {task.task_id}: {len(upcoming_steps)}")
upcoming_steps[0]

step_output = agent.run_step(
    task.task_id, input="Quelles sont toutes les questions posées dans le document à la page 1"
)

step_output = agent.run_step(task.task_id)
print(step_output.is_last)

response = agent.finalize_response(task.task_id)

print(str(response))