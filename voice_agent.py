import asyncio
import re
import speech_recognition as sr
import edge_tts

from playsound3 import playsound
from langchain_ollama import ChatOllama

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
# LangGraph State
# ----------------------------------

class AgentState(TypedDict):
    question: str
    route: str
    answer: str

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
            "divided by"
        ]
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
            .replace("x", "*")
            .replace("times", "*")
            .replace("multiply", "*")
            .replace("multiplied by", "*")
            .replace("divided by", "/")
        )

        result = eval(
            expression
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
# Build Graph
# ----------------------------------
history = []
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

        print(
            f"\nYou: {question}"
        )

        # ----------------------------------
        # Exit
        # ----------------------------------

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

        # ----------------------------------
        # LangGraph Invoke
        # ----------------------------------

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

        # ----------------------------------
        # Speak Response
        # ----------------------------------

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