# for conversational aspects of sami
# depending on what the player responds with,
# trigger a certain reaction or behavior


import os

import speech_recognition as sr

r = sr.Recognizer()

with sr.Microphone() as source:
    print("Say something")
    audio = r.listen(source)

while r.recognize_sphinx(audio) != "goodbye":
    try:
        print("Sphinx thinks you said " + r.recognize_sphinx(audio))
    except sr.UnknownValueError:
        print("Sphinx could not understand audio")
    except sr.RequestError as e:
        print("Sphinx error; {0}".format(e))
