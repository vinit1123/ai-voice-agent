from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="llama3.2"
)

history = []

def ask_agent(question):

    history.append(
        f"User: {question}"
    )

    prompt = f"""
Conversation:

{chr(10).join(history)}

Answer the latest question.
"""

    response = llm.invoke(
        prompt
    )

    answer = response.content

    history.append(
        f"Assistant: {answer}"
    )

    return answer