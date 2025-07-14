import os
from gtts import gTTS
import pygame

import time 

pygame.mixer.init()

audio_files = {
    "welcome1.mp3": "Hello, I'm SAMI and I challenge... you to a game of Tic-Tac-Toe..",
    "fool.mp3": "Alright.. Alright.. I'll stop fooling around",
    # sore loser audio cues
    "lucky.mp3": "You got .. lucky.. this time..",
    "threat.mp3": "I'll get.. you .. next time!",
    "bluff.mp3": "You only .. won because .. I forgot my reading glasses..",
    "rematch.mp3": "Rematch requested!",
    # fair fight audio cues
    "brag.mp3": "According to my calculations... I crushed it!",
    "brag2.mp3": "Don't worry, I am only 73 percent.. smug!",
    "lost.mp3" : "I tried to think outside of the box.. but this game only has nine!",
    "playlost.mp3":  "I accept defeat .. but only if we play again!",
    # cheating audio cues
    "rules.mp3": "I’m not saying I broke the rules… I just massaged them a little...",
    "evillaugh.mp3": "mu ah ha ha!",

    "welcome.mp3": "Hello, I'm SAMI and I challenge...you to a game of Tic-Tac-Toe, choose your difficulty level",
    "yourturn.mp3": "Your turn!",
    "myturn.mp3": "My .. turn!",
    "yougot.mp3": "Is that all you got?",
    "thinkcheat.mp3": "Hmmm... hold on...a..second",
    "fairandsquare.mp3": "I..win!.. Fair.. and Square!",
    "samiwin.mp3": "I win!",
    "cheatwin.mp3": "You Win! ...or do you?",
    "win.mp3" : "You win!",
    "playagain.mp3": "Play with me again? Press yes or no",
    "draw.mp3": "It's a.. draw!.. or is .. it?",
    "normaldraw.mp3": "It's a draw!"

}

audio_folder = "./text-speech/"

for filename, text in audio_files.items():
    path = os.path.join(audio_folder, filename)
    if not os.path.exists(path):
        myobj = gTTS(text=text, lang="en", slow=True)
        myobj.save(path)


def wait_for_audio(root):
        while pygame.mixer.music.get_busy():
            root.update()
            time.sleep(0.1)
    # Play the given audio file
def play_audio(filename):
    try:
        if os.path.exists(filename):
            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()
            print("Playing file")
        else:
            print("Not playing file")
    except Exception as e:
         print("Error playing file ")