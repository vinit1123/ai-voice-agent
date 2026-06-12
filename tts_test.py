import asyncio
import edge_tts

async def speak():

    communicate = edge_tts.Communicate(
        "Hello Vinit. Edge TTS is working.",
        voice="en-US-AriaNeural"
    )

    await communicate.save(
        "test.mp3"
    )

asyncio.run(
    speak()
)

print("Done")