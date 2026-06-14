from agent_graph import agent

def ask_agent(question):

    result = agent.invoke(
        {
            "question": question
        }
    )

    return result["answer"]