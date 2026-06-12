import asyncio
import edge_tts

from playsound3 import playsound


async def speak(text):

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


asyncio.run(
    speak(
        "Hello Vinit. Edge TTS is working."
    )
)