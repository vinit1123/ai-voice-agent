import asyncio
import speech_recognition as sr
import edge_tts

from playsound3 import playsound
from langchain_ollama import ChatOllama

# ----------------------------------
# LLM
# ----------------------------------

llm = ChatOllama(
    model="llama3.2"
)

# ----------------------------------
# Speech Recognition
# ----------------------------------

recognizer = sr.Recognizer()

# ----------------------------------
# Memory
# ----------------------------------

history = []

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
        # Memory Update
        # ----------------------------------

        history.append(
            f"User: {question}"
        )

        prompt = f"""
You are a helpful AI voice assistant.

Keep answers short.
Maximum 2 sentences.

Conversation History:

{chr(10).join(history)}

Answer ONLY the latest user question.
"""

        response = llm.invoke(
            prompt
        )

        answer = response.content.strip()

        history.append(
            f"Assistant: {answer}"
        )

        print(
            f"\nAI: {answer}"
        )

        print(
            f"\nSpeaking..."
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