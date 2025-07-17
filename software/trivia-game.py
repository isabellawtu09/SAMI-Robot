# there will be two modes of trivia
# - hard -> no multiple choice -> one with reward one without reward
# - easy -> multiple choice -> one with reward one without reward

import tkinter as tk 
from tkinter import messagebox, font

# going to add audio to prototype interaction during trivia
# using same gtts with tic tac toe 
# also going to add progress bar to this one 



def show_main_screen():
    welcome.destroy()
    root.deiconify()
    

root = tk.Tk()
root.title("Trivia Game")
root.geometry("300x150")

prompt_label = tk.Label(root, text="Welcome! Ready to play trivia?")
prompt_label.pack(pady=20)
start_button = tk.Button(root, text = "Play Trivia" , command = start_trivia)
start_button.pack(pady=10)

root.mainloop()