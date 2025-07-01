

import tkinter as tk
from tkinter import font
from tkinter import messagebox
import time
from SAMIControl import SAMIControl

from audio_manager import AudioManager

# ideas:
# - create messagebox once round is done to prompt user
# to play again instead of having it throughout the entire gameplay
    # - messagebox on tkinter dimensions cant be manipulated
    # might have to change to something else

# TO DO -
# design interactions, different cheating conditions
# use functions from audio manager for audio probability
# change messagebox to something more visible


# states
# 1 - cheating SAMI
# 2 - Non-cheating SAMI
# 3 - SAMI loses on purpose


# functions needed -
# SAMI Behavior function
# Cleanup function for robot instance
# automated cheating behaviors at a given moment(round,,, etc)


class TicTacToeBoard(tk.Tk):
    # The board's attributes
    def __init__(self):
        super().__init__()
        self.title("Tic-Tac-Toe")
        self.geometry("600x800")
        self._cells = {}
        self.bg_color = "#9d9fa3"
        self.configure(bg= self.bg_color)
        self.player_colors = {
            "X": "#f59342",
            "O" : "#e0484a"
        }
        # Default beginner is the human user
        self.current_player = "X"
        self.buttons_pressed = []

        # Initialize SAMI control instance
        self.robot = SAMIControl(
                arduino_port='COM6',
                 baud_rate=115200,
                 joint_config_file='Joint_config.json',
                 behavior_folder='behaviors',
                 emote_file='Emote.json',
                 audio_folder='audio',
                 starting_voice='Matt'
        )
        # create connection
        self.robot.initialize_serial_connection()
        self._create_widgets()

        self.audio = AudioManager(
            starting_voice_type= "DefaultVoice",
            audio_folder_path='audio'
        )

    # Creation of the "button" widgets to
    # place the player's move
    def _create_widgets(self):
        # Creation of title
        self.display = tk.Label(
            master=self,
            text="Player X's Turn",
            font=font.Font(size=28, weight='bold')
        )
        self.display.pack(pady=20)

        # Game grid
        self.main_container = tk.Frame(master=self, bg="#9d9fa3")
        # Packs frame with content
        self.main_container.pack(expand = True, fill=tk.BOTH, padx=20, pady=20)

        self.grid_frame = tk.Frame(master=self.main_container)
        self.grid_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.button_identities = []

        for row in range(3):
            for col in range(3):
                idx = row * 3 + col
                button = tk.Button(
                    master=self.grid_frame,
                    text='',
                    font=font.Font(size=72, weight='bold'),
                    width=3,
                    height=1,
                    command=lambda idx=idx: self.on_button_press(idx),
                    bg = "#c3c4c7"
                )
                button.grid(row=row, column=col, padx=5, pady=5)
                # Each cell is a button
                self.button_identities.append(button)

    def robot_move(self):
        # Delay after humans move
        self.after(800)
        # Starting behavior for SAMI to do before making move
        self.robot.start_behavior("Wave.json")
        self.audio.send_audio('GameIntro_matt')
        time.sleep(14)
        self.robot.start_behavior("Home.json")
        # Make sure move is done or stop it before moving on to next move
        # then send it back to home
        # Store empty spaces

        empty_spot = [i for i, btn in enumerate(self.button_identities)
                      if btn['text'] == '']
        # Pick first empty spot encountered
        if empty_spot and self.check_winner() is None:
            # Replace with minimax algorithm ? idk yet, some other functions could also be useful
            move_idx = empty_spot[0]
            # Move robots "O" move into corresponding widget "cell"
            button = self.button_identities[move_idx]
            button.config(text=self.current_player , fg = self.player_colors[self.current_player])
            self.buttons_pressed.append(move_idx)
        # Check board state before continuing game
        winner = self.check_winner()
        if winner:
            # My/your turn instead of player {} turn for less confusion?
            self.display.config(text= f"SAMI Wins!")
            # self.robot.start_behavior("Home.json")
            # Delays
            self.after(1000, self.play_again)
        elif len(self.buttons_pressed) == 9:
            self.display.config(text = "It's a Draw!")
            # self.robot.start_behavior("Home.json")
            self.after(1000, self.play_again)
        else:
            # Return back to human player if no one has won
            self.current_player = "X"
            self.display.config(text = f"Player { self.current_player}'s Turn")
    # Recieves the state of the board in which robot or human won
    # highlights those cells
    def highlight_win(self, a, b, c):
        highlight_color = "#807878"
        # Change the background color of the winning cells for visibility
        self.button_identities[a].config(bg=highlight_color)
        self.button_identities[b].config(bg=highlight_color)
        self.button_identities[c].config(bg=highlight_color)
    # Human moves
    def on_button_press(self, idx):
        button = self.button_identities[idx]

        if button['text'] == '' and self.check_winner() is None:
            button.config(text=self.current_player, fg = self.player_colors[self.current_player])
            self.buttons_pressed.append(idx)
            # Check the state of board for winner before continuing
            winner = self.check_winner()
            if winner:
                self.display.config(text=f"You Win!")
                # self.robot.start_behavior("Home.json")
                self.after(1000, self.play_again)
                # Behavior from SAMI afterwards
            elif len(self.buttons_pressed) == 9:
                self.display.config(text="It's a Draw!")
                # self.robot.start_behavior("Home.json")
                self.after(1000, self.play_again)
                # Behavior from SAMI afterwards
            else:
                self.current_player = "O" if self.current_player == "X" else "X"
                self.display.config(text=f"SAMI's {self.current_player} Turn")
                # Delay before making the robot's move
                # Behavior from SAMI before
                self.after(500, self.robot_move)

    def check_winner(self):
        board = [btn['text'] for btn in self.button_identities]
        wins = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # columns
            [0, 4, 8], [2, 4, 6]              # diagonals
        ]
        for a, b, c in wins:
            if board[a] == board[b] == board[c] != '':
                self.highlight_win(a, b, c)
                return board[a]
        return None

    def restart_game(self):
        for button in self.button_identities:
            button.config(text='')
        for row in range(3):
            for col in range(3):
                idx = row * 3 + col
                button = self.button_identities[idx]
                button.config(text='', bg="#c3c4c7")
        self.buttons_pressed.clear()
        self.current_player = "X"
        self.display.config(text="Player X's Turn")

    def play_again(self):
        # popup = tk.Toplevel()
        # popup.geometry()
        self.after(1000)
        result = tk.messagebox.askquestion(title=None, message="Play with me again?", type = "yesno")
        # Restart the game and clear any highlighted cells etc.
        if result == "yes":
            self.restart_game()
        else:
            # Dont do anything, maintain board state
            pass

if __name__ == "__main__":
    game = TicTacToeBoard()
    game.mainloop()
    # close connection here with the SAMIControl function 
