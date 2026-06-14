from typing import TypedDict
from langchain_ollama import ChatOllama
from langchain_ollama import (
    OllamaEmbeddings
)

from langchain_community.document_loaders import (
    PyPDFLoader
)

from langchain_text_splitters import (
    RecursiveCharacterTextSplitter
)

from langchain_community.vectorstores import (
    FAISS
)

llm = ChatOllama(
    model="llama3.2"
)

history = []

class AgentState(TypedDict):

    question: str
    route: str
    answer: str
    from typing import TypedDict

class AgentState(TypedDict):

    question: str
    route: str
    answer: str


def supervisor(state):

    q = state["question"].lower()

    if any(
        word in q
        for word in [
            "+",
            "-",
            "*",
            "/",
            "x",
            "times",
            "multiply",
            "multiplied by",
            "divided by",
            "into"
        ]
    ):

        return {
            "route": "tool"
        }

    rag_keywords = [
        "attention",
        "transformer",
        "encoder",
        "decoder",
        "multi head",
        "paper"
    ]

    if any(
        word in q
        for word in rag_keywords
    ):

        return {
            "route": "rag"
        }

    return {
        "route": "chat"
    }
def tool_agent(state):

    try:

        expression = (
            state["question"]
            .lower()
            .replace("what is", "")
            .replace("calculate", "")
            .replace("multiplied by", "*")
            .replace("multiply", "*")
            .replace("times", "*")
            .replace("x", "*")
            .replace("divided by", "/")
            .strip()
        )

        print(
            f"\nExpression: {expression}"
        )

        result = eval(
            expression
        )

        return {
            "answer": str(result)
        }

    except Exception as e:

        print(
            f"\nTool Error: {e}"
        )

        return {
            "answer": "Invalid calculation"
        }
    
loader = PyPDFLoader(
    "data/sample.pdf"
)

docs = loader.load()

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=200
)

chunks = splitter.split_documents(
    docs
)

embeddings = OllamaEmbeddings(
    model="nomic-embed-text"
)

vectorstore = FAISS.from_documents(
    chunks,
    embeddings
)

retriever = vectorstore.as_retriever(
    search_kwargs={"k": 5}
)
def chat_agent(state):

    history.append(
        f"User: {state['question']}"
    )

    prompt = f"""
You are a helpful AI assistant.

Keep answers short.

Conversation:

{chr(10).join(history)}

Answer only the latest question.
"""

    response = llm.invoke(
        prompt
    )

    answer = response.content

    history.append(
        f"Assistant: {answer}"
    )

    return {
        "answer": answer
    }
#------------------------
# Rag Agent
#----------------------------
def rag_agent(state):

    docs = retriever.invoke(
        state["question"]
    )

    context = "\n\n".join(
        doc.page_content
        for doc in docs
    )

    prompt = f"""
Answer using ONLY the context.

Context:

{context}

Question:

{state["question"]}

Answer:
"""

    response = llm.invoke(
        prompt
    )

    return {
        "answer": response.content
    }
#--------------------------------------
# Chat Agent 
#-------------------------------------
    def chat_agent(state):

        history.append(
        f"User: {state['question']}"
    )

    prompt = f"""
You are a helpful AI assistant.

Conversation History:
{chr(10).join(history)}

IMPORTANT:
Answer ONLY the latest user question.
Do not repeat conversation history.
Do not repeat previous answers.

Latest User Question:
{state["question"]}
"""

    response = llm.invoke(
        prompt
    )

    answer = response.content.strip()

    history.append(
        f"Assistant: {answer}"
    )

    return {
        "answer": answer
    }
from langgraph.graph import (
    StateGraph,
    END
)

def router(state):

    return state["route"]


graph = StateGraph(
    AgentState
)

graph.add_node(
    "supervisor",
    supervisor
)

graph.add_node(
    "chat_agent",
    chat_agent
)

graph.add_node(
    "tool_agent",
    tool_agent
)

graph.add_node(
    "rag_agent",
    rag_agent
)

graph.set_entry_point(
    "supervisor"
)

graph.add_conditional_edges(
    "supervisor",
    router,
    {
        "chat": "chat_agent",
        "tool": "tool_agent",
        "rag": "rag_agent"
    }
)

graph.add_edge(
    "chat_agent",
    END
)

graph.add_edge(
    "tool_agent",
    END
)

graph.add_edge(
    "rag_agent",
    END
)

agent = graph.compile()
if __name__ == "__main__":

    result = agent.invoke(
        {
            "question": "2 multiply 3"
        }
    )

    print(result)