import speech_recognition as sr

r = sr.Recognizer()

with sr.Microphone() as source:

    print("Speak now...")

    audio = r.listen(source)

print("Processing...")

text = r.recognize_google(audio)

print("You said:")
print(text)
import speech_recognition as sr

r = sr.Recognizer()

with sr.Microphone() as source:

    print("Speak now...")

    audio = r.listen(source)

print("Processing...")

text = r.recognize_google(audio)

print("You said:")
print(text)