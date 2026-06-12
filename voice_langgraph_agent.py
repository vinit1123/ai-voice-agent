from typing import TypedDict
import re

from langgraph.graph import (
    StateGraph,
    END
)

from langchain_ollama import ChatOllama

# ----------------------------------
# LLM
# ----------------------------------

llm = ChatOllama(
    model="llama3.2"
)

# ----------------------------------
# State
# ----------------------------------

class AgentState(TypedDict):
    question: str
    route: str
    answer: str

# ----------------------------------
# Supervisor
# ----------------------------------

def supervisor(state):

    q = state["question"]

    if re.fullmatch(
        r"[0-9\s\+\-\*\/\.\(\)]+",
        q.strip()
    ):

        return {
            "route": "tool"
        }

    return {
        "route": "chat"
    }

# ----------------------------------
# Chat Agent
# ----------------------------------

def chat_agent(state):

    response = llm.invoke(
        state["question"]
    )

    return {
        "answer": response.content
    }

# ----------------------------------
# Tool Agent
# ----------------------------------

def tool_agent(state):

    try:

        result = eval(
            state["question"]
        )

        return {
            "answer": str(result)
        }

    except:

        return {
            "answer": "Invalid calculation"
        }

# ----------------------------------
# Router
# ----------------------------------

def router(state):

    return state["route"]

# ----------------------------------
# Graph
# ----------------------------------

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

graph.set_entry_point(
    "supervisor"
)

graph.add_conditional_edges(
    "supervisor",
    router,
    {
        "chat": "chat_agent",
        "tool": "tool_agent"
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

agent = graph.compile()

# ----------------------------------
# Test
# ----------------------------------

while True:

    question = input(
        "\nYou: "
    )

    if question.lower() == "exit":
        break

    result = agent.invoke(
        {
            "question": question
        }
    )

    print(
        f"\nRoute: {result['route']}"
    )

    print(
        f"Answer: {result['answer']}"
    )