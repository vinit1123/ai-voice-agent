import asyncio
import speech_recognition as sr
import edge_tts
from memory import (
    save_memory,
    get_memories
)
from playsound3 import playsound

from langchain_ollama import (
    ChatOllama,
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

from typing import TypedDict

from langgraph.graph import (
    StateGraph,
    END
)

# ----------------------------------
# LLM
# ----------------------------------

llm = ChatOllama(
    model="llama3.2"
)

# ----------------------------------
# RAG Setup
# ----------------------------------

loader = PyPDFLoader(
    "data/sample.pdf"
)

docs = loader.load()

splitter = (
    RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=200
    )
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

retriever = (
    vectorstore.as_retriever(
        search_kwargs={"k": 5}
    )
)

# ----------------------------------
# LangGraph State
# ----------------------------------

class AgentState(TypedDict):

    question: str
    route: str
    answer: str

# ----------------------------------
# Memory
# ----------------------------------

history = []

# ----------------------------------
# Supervisor
# ----------------------------------

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

# ----------------------------------
# Chat Agent
# ----------------------------------
memories = get_memories()

print(
    "\nMEMORIES:"
)

for m in memories[-5:]:

    print(m)
def chat_agent(state):

    history.append(
        f"User: {state['question']}"
    )

    prompt = f"""
You are a helpful AI voice assistant.

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

# ----------------------------------
# Tool Agent
# ----------------------------------

def tool_agent(state):

    try:

        expression = (
            state["question"]
            .lower()
            .replace("what is", "")
            .replace("calculate", "")
            .replace("x", "*")
            .replace("times", "*")
            .replace("multiplied by", "*")
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
# ----------------------------------
# RAG Agent
# ----------------------------------

def rag_agent(state):

    docs = retriever.invoke(
        state["question"]
    )

    print("\n===== RETRIEVED DOCS =====\n")

    for i, doc in enumerate(docs):

        print(
            f"\nChunk {i+1}:\n"
        )

        print(
            doc.page_content[:500]
        )

    context = "\n\n".join(
        doc.page_content
        for doc in docs
    )

    prompt = f"""
Answer the question using ONLY the context below.

Do not use outside knowledge.

If the answer is not found in the context,
reply exactly:

I could not find that information in the PDF.

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


# ----------------------------------
# Router
# ----------------------------------

def router(state):

    return state["route"]

# ----------------------------------
# Build Graph
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

# ----------------------------------
# Speech Recognition
# ----------------------------------

recognizer = sr.Recognizer()

# ----------------------------------
# Edge TTS
# ----------------------------------

async def speak_async(text):

    communicate = edge_tts.Communicate(
        text,
        voice="en-US-AriaNeural"
    )

    await communicate.save(
        "response.mp3"
    )

    playsound(
        "response.mp3"
    )

def speak(text):

    asyncio.run(
        speak_async(text)
    )

# ----------------------------------
# Main Loop
# ----------------------------------

while True:

    try:

        with sr.Microphone() as source:

            print("\n🎤 Speak...")

            recognizer.adjust_for_ambient_noise(
                source,
                duration=1
            )

            audio = recognizer.listen(
                source,
                timeout=5,
                phrase_time_limit=10
            )

        question = recognizer.recognize_google(
            audio
        )
        save_memory(question)
        print(
            f"\nYou: {question}"
        )

        if question.lower() in [
            "exit",
            "quit",
            "stop"
        ]:

            print(
                "\nGoodbye!"
            )

            speak(
                "Goodbye Vinit"
            )

            break

        result = agent.invoke(
            {
                "question": question
            }
        )

        answer = result["answer"]

        route = result["route"]

        print(
            f"\nRoute: {route.upper()}"
        )

        print(
            f"\nAI: {answer}"
        )

        print(
            "\nSpeaking..."
        )

        speak(
            answer
        )

    except sr.UnknownValueError:

        print(
            "\nCould not understand audio"
        )

    except sr.WaitTimeoutError:

        print(
            "\nListening timeout"
        )

    except KeyboardInterrupt:

        print(
            "\nStopped by user"
        )

        break

    except Exception as e:

        print(
            f"\nError Type: {type(e).__name__}"
        )

        print(
            f"Error Message: {str(e)}"
        )