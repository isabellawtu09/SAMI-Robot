import os
from gtts import gTTS
import pygame

import time 

pygame.mixer.init()

audio_files = {
     #Final game audio
     "youchampion.mp3" : "You are the champion!",
     "mechampion.mp3" : "I am the champion",
     "tiegame.mp3" : "It's a tie!",
     # Round  audio 
     "1.mp3": "Round one!",
     "2.mp3": "Round two!",
     "3.mp3": "Round three!",
     "round1.mp3" : "Round one complete!",
     "round2.mp3" : "Round two complete!",
     "round3.mp3" : "Round three complete!",
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
    "normaldraw.mp3": "It's a draw!",

    # Round summary audio - if sami lost
    "roundwon.mp3": "You win this round!",
    "roundwon1.mp3" : "Don't get used to it.. this was just my warm-up round",
    "roundwon2.mp3" : "I'd clap but I'm too busy preparing my comeback!",
    "roundwon3.mp3" : "But did you win?.. or did I just lose in a very generous way? ",
    "roundwon4.mp4" : "I must be low on battery..",
    "roundwon5.mp3" : "Okay, you win the battle, but not the war. Next round?",
    # Round summary audi - if sami won
    "roundlost.mp3" : "I win this round!",
    "roundlost1.mp3" : "I'm not saying I'm better but..the scoreboard is!",
    "roundlost2.mp3" : "Where's my trophy?",
    "roundlost3.mp3" : "Let’s see if you can even the score!",
    "roundlost4.mp3" : "I hope you’re not tired already — I play better when you fight back!",
    "roundlost5.mp3" : "You're making me look too good, come on, bring your A-game!",
    # Sami lost the overall game
    "lostgame.mp3": "You win!",
    "lostgame1.mp3":  "I accept defeat .. but only if we play again!",
    "lostgame2.mp3" : "I’m officially challenging you to a rematch — don’t keep me waiting!",
    "lostgame3.mp3" : "Alright, you win this one — but I’m coming back stronger next game!",
    "lostgame4.mp3" : "But I didn't lose, I’m just giving you a confidence boost.",
    # Sami won the overall game
    "wongame.mp3": "I win!",
    "wongame1.mp3" : "And that, my friend, is how it’s done!",
    "wongame2.mp3" : "I’m just getting started — think you can handle another game?"
    # "wongame3.mp3" : "",
    # "wongame4.mp3" : "",
    # "wongame5.mp3" : "If you’re not scared yet, you should be — let’s go again!",
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