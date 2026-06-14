import streamlit as st
import speech_recognition as sr
import edge_tts
import asyncio

from agent_backend import ask_agent

# ----------------------------------
# Page Config
# ----------------------------------

st.set_page_config(
    page_title="AI Voice Agent",
    page_icon="🤖"
)

st.title("🤖 AI Voice Agent")

#---------------------
# Helper function 
#---------------------
async def generate_audio(text):

    communicate = edge_tts.Communicate(
        text,
        voice="en-US-AriaNeural"
    )

    await communicate.save(
        "response.mp3"
    )


def speak(text):

    asyncio.run(
        generate_audio(text)
    )
# ----------------------------------
# Voice Input
# ----------------------------------

audio = st.audio_input(
    "🎤 Speak"
)

if audio:

    try:

        with open(
            "temp.wav",
            "wb"
        ) as f:

            f.write(
                audio.getbuffer()
            )

        recognizer = sr.Recognizer()

        with sr.AudioFile(
            "temp.wav"
        ) as source:

            audio_data = recognizer.record(
                source
            )

        text = recognizer.recognize_google(
            audio_data
        )

        st.success(
            f"You Said: {text}"
        )

        answer = ask_agent(
            text
        )

        st.write(
            f"🤖 {answer}"
        )

        speak(answer)

        with open(
            "response.mp3",
            "rb"
        ) as audio_file:

            st.audio(
                audio_file.read(),
                format="audio/mp3"
            )

    except Exception as e:

        st.error(
            f"Error: {str(e)}"
        )

# ----------------------------------
# Text Input
# ----------------------------------

question = st.text_input(
    "Ask Something"
)

if st.button(
    "Send"
):

    answer = ask_agent(
        question
    )

    st.write(
        f"🤖 {answer}"
    )