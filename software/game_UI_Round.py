import tkinter as tk
from tkinter import ttk
from tkinter import font
import random
import os

# any text/audio that isnt directly "game" related

# game imports
from computer_audio import wait_for_audio, play_audio, audio_files
from cheating_animator import CheatingAnimator
from difficulty_manager import DifficultyManager
# sami imports
from SAMIControl import SAMIControl
from audio_manager import AudioManager

class TicTacToeBoard(tk.Tk):
    def __init__(self, default_difficulty=None):
        super().__init__()

        # Initialize SAMI control instance
        # self.robot = SAMIControl(
        #         arduino_port='COM6',
        #          baud_rate=115200,
        #          joint_config_file='Joint_config.json',
        #          behavior_folder='behaviors',
        #          emote_file='Emote.json',
        #          audio_folder='audio',
        #          starting_voice='Matt'
        # )
        # Create connection
        #self.robot.initialize_serial_connection()

        # self.audio = AudioManager(
        #     starting_voice_type= "DefaultVoice",
        #     audio_folder_path='audio'
        # )

        play_audio("./text-speech/welcome1.mp3")
        self.title("Tic-Tac-Toe")
        self.samicount = 0
        self.samiWon = 0
        self.playerWon = 0
        self.win_count = 0
        self.drawRound = 0
        self.cheating_animator = CheatingAnimator(self)
        self.sami_turn_progress = False
        self.geometry("800x900")
        self._cells = {}
        self.bg_color = "#96969C"
        self.configure(bg= self.bg_color)
        self.current_round = 1
        self.max_round = 3
        self.player_colors = {
            "X": "#EF7A06",
            "O" : "#721817"
        }

        # Manually set difficulty sequence
        self.difficulty_sequence = (
        # verbal and physical cues to create 
        # transition between the previous and following game
        # especially if a new condition will be setup 
        ["easy"] * 1 +
        ["normal"] * 3 +
        ["hard"] * 2 +
        ["normal"] * 2 +
        ["hard"] * 1
        )
        self.difficulty_seq_index = 0

        self.current_player = "X"
        self.buttons_pressed = []
        self.current_difficulty = None
        self.game_started = False

        self.animation_in_progress = False
        self.animation_steps = 0
        self.animation_delay = 90

        self.games_per_round = 3
        self.current_round = 1
        self.round_scores = {'player': 0, 'sami': 0, 'draws': 0}

        self.difficulty_manager = DifficultyManager(
             game_instance = self
        #     sami_control = self.robot,
        #     audio_manager = self.audio,
        )
        self._show_start_button(default_difficulty)


    def _show_start_button(self, default_difficulty):
        for widget in self.winfo_children():
            widget.destroy()

            # Welcome message
        splash_label = tk.Label(
            master=self,
            text="Hello I'm SAMI and I challenge you\n to a game of Tic-Tac-Toe!",
            font=font.Font(family="Helvetica",size=40, weight='bold'),
            bg="#96969C",
            fg='black'
        )
        splash_label.pack(pady=(100, 20))
            # Start button
        start_button = tk.Button(
            master=self,
            text="Start Game",
            font=font.Font(size=28, weight='bold'),
            width=15,
            height=2,
            command=lambda: self.start_game(default_difficulty if default_difficulty else "easy"),
            bg="#f59342",
            fg="black",
            relief="raised",
            bd=4
        )
        start_button.pack(pady=40)

    def advance_difficulty_sequence(self):
        if self.difficulty_seq_index < len(self.difficulty_sequence):
            next_diff = self.difficulty_sequence[self.difficulty_seq_index]
            self.set_difficulty(next_diff)
            self.difficulty_seq_index += 1
        else:
            # Sequence complete - show final results
            self.show_score()
            return

    # # Creates the final state of the board to then show after cheating sequence
    def create_cheating_board_state(self, current_board):
        new_board = [""] * 9  # Start with empty board

        # Create a winning configuration for SAMI
        winning_lines = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # columns
            [0, 4, 8], [2, 4, 6]              # diagonals
        ]

        # Choose a random winning line for SAMI
        chosen_line = random.choice(winning_lines)

        # Place SAMI pieces in the winning line
        for pos in chosen_line:
            new_board[pos] = "O"

        # Place some user pieces in non-winning positions to make it look realistic
        user_pieces_to_place = min(3, len([val for val in current_board if val == "X"]))
        empty_positions = [i for i, val in enumerate(new_board) if val == ""]

        for _ in range(user_pieces_to_place):
            if empty_positions:
                pos = random.choice(empty_positions)
                new_board[pos] = "X"
                empty_positions.remove(pos)

        return new_board

    def cheat_after_user_win(self):
        current_board = [btn['text'] for btn in self.button_identities]
        cheating_board = self.create_cheating_board_state(current_board)

        # Ensure buttons stay disabled during cheating animation
        self.sami_turn_progress = True
        self.disable_buttons()
        # Start the cheating animation
        self.cheating_animator.rearrange_board_animation(cheating_board)

    def start_game(self, difficulty):

        self.current_round = 1
        self.round_scores = {'player': 0, 'sami': 0, 'draws': 0}
        self.set_difficulty(difficulty)
        self._create_widgets()
        play_audio(f'./text-speech/{self.current_round}.mp3')  # <-- Add this line
        wait_for_audio(self) 
        self.restart_game()
        self.update_idletasks()  # <-- Force the board to render

    # Creation of the "button" widgets to
    # place the player's move
    def _create_widgets(self):
        for widget in self.winfo_children():
            widget.destroy()
        # Create score display frame at the top
        self.score_frame = tk.Frame(master=self, bg="#96969C")
        self.score_frame.pack(pady=(20, 10))

        # Player score (X)
        self.player_score_label = tk.Label(
            master=self.score_frame,
            text=f"You : {self.win_count}",
            font=font.Font(size=20, weight='bold'),
            bg= "white",
            fg=self.player_colors["X"],
            width=12,
            relief="ridge",
            bd=3
        )
        self.player_score_label.pack(side=tk.LEFT, padx=20)
        
        # Round indicator
        self.round_label = tk.Label(
            master=self.score_frame,
            text=f"Round {self.current_round}",
            font=font.Font(size=18, weight='bold'),
            bg='white',
            fg='black',
            width=10,
            relief="ridge",
            bd=3
        )
        self.round_label.pack(side=tk.LEFT, padx=20)
        
        # SAMI score (O)
        self.sami_score_label = tk.Label(
            master=self.score_frame,
            text=f"SAMI : {self.samicount}",
            font=font.Font(size=20, weight='bold'),
            bg="white",
            fg=self.player_colors["O"],
            width=12,
            relief="ridge",
            bd=3
        )
        self.sami_score_label.pack(side=tk.LEFT, padx=20)

        # Turn display
        self.display = tk.Label(
            master=self,
            text="Your Turn",
            font=font.Font(size=28, weight='bold')
        )
        self.display.pack(pady=20)
        self.after(100, play_audio("./text-speech/yourturn.mp3"))

        # Game grid
        self.main_container = tk.Frame(master=self, bg="#96969C")
        self.main_container.pack(expand=True, fill=tk.BOTH, padx=30, pady=30)

        self.grid_frame = tk.Frame(
            master=self.main_container,
            bg = "#96969C",
            bd=6,
            relief="ridge"
            )
        self.grid_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        #self.grid_frame.pack(expand=True, fill =tk.BOTH, padx=30, pady=30)
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
                    bg="#c3c4c7",
                    bd=3,
                    relief="ridge"
                )
                button.grid(row=row, column=col, padx=5, pady=5)
                self.button_identities.append(button)

    def update_score_display(self):
        # Update score labels

        if hasattr(self, 'player_score_label'):
            self.player_score_label.config(text=f"You : {self.win_count}")
        if hasattr(self, 'sami_score_label'):
            self.sami_score_label.config(text=f"SAMI : {self.samicount}")
        if hasattr(self, 'round_label'):
            self.round_label.config(text=f"Round: {self.current_round}")

    def robot_move(self):
        # Getting current board state to send to difficulty level
        board = [btn['text'] for btn in self.button_identities]
        move_idx = self.difficulty_manager.get_move(board)

        # If robot move is valid
        if move_idx is not None:
            # Make SAMI's move
            button = self.button_identities[move_idx]
            button.config(text="O", fg = self.player_colors["O"])
            self.buttons_pressed.append(move_idx)

            # This should be a calculated move instead of a random move
            if random.random() < 0.30 and self.current_difficulty == "hard":
                available2ndmove = [i for i, btn in enumerate(self.button_identities)
                                    if btn['text'] == '' and i != move_idx]
                if available2ndmove:
                    s2ndmove = random.choice(available2ndmove)
                    self.after(300)
                    button2 = self.button_identities[s2ndmove]
                    play_audio("./text-speech/evillaugh.mp3")
                    wait_for_audio(self)
                    button2.config(text="O", fg=self.player_colors["O"])
                    self.buttons_pressed.append(s2ndmove)

        # Check board state before continuing game
        winner = self.check_winner()
        if winner:
            # My/your turn instead of player {} turn for less confusion?
            self.display.config(text= f"I win!")
            self.samicount += 1
            self.round_scores['sami'] += 1
            self.update_score_display()  # Update score display
            play_audio("./text-speech/samiwin.mp3")
            wait_for_audio(self)
            # self.robot.start_behavior("Home.json")
            # Delays
            self.sami_turn_progress = False  # Reset flag before delay
            self.enable_buttons()  # Re-enable buttons
            self.after(1000, self.play_again)
        elif all(btn['text'] != '' for btn in self.button_identities):
            if self.current_difficulty == "hard":
                self.display.config(text = "It's a Draw!.. or is it?")
                self.round_scores['draws'] += 1
                self.update_score_display()  # Update score display
                play_audio("./text-speech/draw.mp3")
                wait_for_audio(self)
                self.sami_turn_progress = False  # Reset flag before delay
                self.after(2000, self.cheat_after_user_win)
                return
            self.display.config(text = "It's a Draw!")
            play_audio("./text-speech/normaldraw.mp3")
            self.round_scores['draws'] += 1
            self.update_score_display()  # Update score display
            wait_for_audio(self)
        
            # self.robot.start_behavior("Home.json")
            self.sami_turn_progress = False  # Reset flag before delay
            self.enable_buttons()  # Re-enable buttons
            self.after(1000, self.play_again)
        else:
            # Return back to human player if no one has won
            # Play "Your turn" audio AFTER SAMI's move
            self.display.config(text="Your Turn")
            self.current_player = "X"
            play_audio("./text-speech/yourturn.mp3")
            wait_for_audio(self)  # Let it finish before giving control
            self.sami_turn_progress = False
            self.enable_buttons()  # Re-enable buttons for user interaction

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
        # User hasn't chosen difficulty level
        if not self.game_started or self.animation_in_progress or self.sami_turn_progress:
            return

        button = self.button_identities[idx]

        if button['text'] == '' and self.check_winner() is None:
            button.config(text="X", fg = self.player_colors["X"])
            self.buttons_pressed.append(idx)

            # Check if this move creates a winning condition
            winner = self.check_winner()

            if winner == "X":
                # User has won! But SAMI will cheat and rearrange the board

                if self.current_difficulty == "hard":
                    self.display.config(text="You Win! ...or do you?")
                    # Wait a moment to let the user see they won, then start cheating
                    play_audio("./text-speech/cheatwin.mp3")
                    wait_for_audio(self)
                    self.after(2000, self.cheat_after_user_win)
                    return
                self.win_count += 1
                self.round_scores['player'] += 1
                self.update_score_display()  # Update score display
                self.display.config(text="You Win!")
                play_audio("./text-speech/win.mp3")
                wait_for_audio(self)
                if random.random() <= 0.5:
                    # randomly choose between the sore loser audios
                    audio = random.choice(["threat.mp3" , "bluff.mp3", "lucky.mp3"])
                    self.display.config(text=audio_files[audio])
                    play_audio(f"./text-speech/{audio}")
                    wait_for_audio(self)
                self.after(1000, self.play_again)
            elif winner == "O":
                self.samicount += 1
                self.round_scores['sami'] += 1
                self.update_score_display()  # Update score display
                self.display.config(text=f"I Win!")
                play_audio("./text-speech/samiwin.mp3")
                wait_for_audio(self)
                self.after(1000, self.play_again)
            elif all(btn['text'] != '' for btn in self.button_identities):
                if self.current_difficulty == "hard":
                    self.display.config(text = "It's a Draw!.. or is it?")
                    self.round_scores['draws'] += 1
                    self.update_score_display()  # Update score display
                    play_audio("./text-speech/draw.mp3")
                    wait_for_audio(self)
                    self.after(2000, self.cheat_after_user_win)
                    return
                self.display.config(text="It's a Draw!")
                play_audio('./text-speech/normaldraw.mp3')
                wait_for_audio(self)
                self.round_scores['draws'] += 1
                self.update_score_display()  # Update score display
                self.after(1000, self.play_again)
            else:
                # Play "My turn" audio BEFORE SAMI's move
                self.display.config(text=f"My Turn")
                self.current_player = "O"

                # Immediately disable buttons and set flag to prevent user interaction
                self.sami_turn_progress = True
                self.disable_buttons()

                # Delay before making the robot's move
                play_audio("./text-speech/myturn.mp3")
                wait_for_audio(self)  # Let audio finish
                self.after(500, self.robot_move)  # Now robot moves

    def check_winner(self):
        board = [btn['text'] for btn in self.button_identities]
        wins = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # columns
            [0, 4, 8], [2, 4, 6]              # diagonals
        ]
        for a, b, c in wins:
            if board[a] == board[b] == board[c] != '':
                # Always highlight winning cells, regardless of difficulty
                self.highlight_win(a, b, c)
                return board[a]
        return None

    def disable_buttons(self):
        
        pass
    
    def enable_buttons(self):
        
        pass

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
        self.sami_turn_progress = False  # Reset turn flag
        self.enable_buttons()  # Ensure buttons are enabled

        self.display.config(text="Your Turn")
        play_audio("./text-speech/yourturn.mp3")
        wait_for_audio(self)
        self.game_started = True  # <-- Add this line

    def set_difficulty(self, new_difficulty):
        if self.current_difficulty != new_difficulty:
            self.current_difficulty = new_difficulty
            self.difficulty_manager.set_difficulties(new_difficulty)
            # Optional: give feedback in the UI
            if hasattr(self, 'display'):
                self.display.config(text=f"Difficulty changed to {new_difficulty.capitalize()}")

    def show_score(self):

        for widget in self.winfo_children():
            widget.destroy()

        score_frame = tk.Frame(self, bg=self.bg_color)
        score_frame.pack(expand=True, fill=tk.BOTH)

        title_label = tk.Label(
            master=score_frame,
            text="Thanks for playing!",
            font=font.Font(size=40, weight="bold"),
            bg= "white",
            fg="black"
        )
        title_label.pack(pady=(60, 20))

        # X's score
        x_label = tk.Label(
            master=score_frame,
            text=f"You (X): {self.win_count}",
            font=font.Font(size=32, weight="bold"),
            bg="white",
            fg=self.player_colors["X"],
            width=20,
            relief="ridge",
            bd=4
        )
        x_label.pack(pady=30)

        # O's score
        o_label = tk.Label(
            master=score_frame,
            text=f"SAMI (O): {self.samicount}",
            font=font.Font(size=32, weight="bold"),
            bg="white",
            fg=self.player_colors["O"],
            width=20,
            relief="ridge",
            bd=4
        )
        o_label.pack(pady=30)

        # Depending on outcome of scores, create an audio cue
        # based on that
        if self.win_count > self.samicount:
            samilost = tk.Label(
            master=score_frame,
            text=f"{audio_files['playlost.mp3']}",
            font=font.Font(size=40, weight="bold"),
            bg= "white",
            fg="black"
        )
            samilost.pack(pady=(60, 20))
            play_audio("./text-speech/playlost.mp3")
            wait_for_audio(self)
        elif self.samicount > self.win_count:
            samiwon = tk.Label(
            master=score_frame,
            text=f"{audio_files['yougot.mp3']}",
            font=font.Font(size=40, weight="bold"),
            bg= "white",
            fg="black"
        )
            samiwon.pack(pady=(60, 20))
            play_audio("./text-speech/yougot.mp3")
            wait_for_audio(self)



    def play_again(self):
        # Automatically continue to next game without message box
        # increment index first
        # Increment index first

    # If all games are done, show final results
        if self.difficulty_seq_index >= len(self.difficulty_sequence):
            self.show_score()
            return

    # Show round summary after every 5 games
        if (self.difficulty_seq_index + 1) % self.games_per_round == 0:
            self.advance_difficulty_sequence()
            self.show_round_summary()
        else:
            self.advance_difficulty_sequence()
            self.restart_game()

    def show_round_summary(self):
        for widget in self.winfo_children():
            widget.destroy()
        if self.current_round < self.max_round:
            # Only update round winners if we're not at the final round
            if self.round_scores['player'] > self.round_scores['sami']:
                self.playerWon += 1
            elif self.round_scores['player'] < self.round_scores['sami']:
                self.samiWon += 1

            summary_frame = tk.Frame(self, bg=self.bg_color)
            summary_frame.pack(expand=True, fill=tk.BOTH, padx=50, pady=50)
            round_label = tk.Label(
                master=summary_frame,
                text=f"Round {self.current_round} Complete!",
                font=font.Font(size=36, weight='bold'),
                bg=self.bg_color,
                fg='white'
            )
            
            round_label.pack(pady=20)
            audio_label = tk.Label(
                master=summary_frame,
                text=audio_files["roundwon.mp3"],
                font=font.Font(size=24, weight='bold'),
                bg= 'white',
                fg='black'
             )
            audio_label.pack(pady=10)
            results_text = f"You: {self.round_scores['player']} | SAMI: {self.round_scores['sami']} | Draws: {self.round_scores['draws']}"
            results_label = tk.Label(
                master=summary_frame,
                text=results_text,
                font=font.Font(size=24),
                bg=self.bg_color,
                fg='white'
            )
            results_label.pack(pady=20)
            continue_button = tk.Button(
                master=summary_frame,
                text="Next Round",
                font=font.Font(size=20, weight='bold'),
                width=15,
                height=2,
                command=self._start_next_round,
                bg="#f59342",
                fg="black",
                relief="raised",
                bd=4
            )
            def show_continue_button():
                continue_button.pack(pady=30)
            audiofile = f"./text-speech/round{self.current_round}.mp3"
            play_audio(audiofile)
            wait_for_audio(self)
            # if player scored more wins then play a sore loser sami audio
            if self.round_scores['player'] > self.round_scores['sami']:
                audio_label.config(text=audio_files["roundwon.mp3"])
                play_audio("./text-speech/roundwon.mp3")
                wait_for_audio(self)
                audionum = random.randint(1,5)

                afile = f"./text-speech/roundwon{audionum}.mp3"
                key = f'roundwon{audionum}.mp3'
                audio_label.config(text=audio_files[key])
                play_audio(afile)
                wait_for_audio(self)
            elif self.round_scores['player'] < self.round_scores['sami']:
                audio_label.config(text=audio_files["roundlost.mp3"])
                play_audio("./text-speech/roundlost.mp3")
                audionum = random.randint(1,5)
                wait_for_audio(self)
                afile = f"./text-speech/roundlost{audionum}.mp3"
                key = f'roundlost{audionum}.mp3'
                audio_label.config(text=audio_files[key])
                play_audio(afile)
                wait_for_audio(self)
            show_continue_button()

        else:
            # Update round winners for the final round
            if self.round_scores['player'] > self.round_scores['sami']:
                self.playerWon += 1
            elif self.round_scores['player'] < self.round_scores['sami']:
                self.samiWon += 1

            winner_text = ""
            if self.playerWon > self.samiWon:
                winner_text = "You are the champion!"
                winner_color = self.player_colors["X"]
                play_audio("./text-speech/youchampion.mp3")
                wait_for_audio(self)
            elif self.samiWon > self.playerWon:
                winner_text = "I am the champion!"
                winner_color = self.player_colors["O"]
                play_audio("./text-speech/mechampion.mp3")
                wait_for_audio(self)
                play_audio("./text-speech/evillaugh.mp3")
            else:
                winner_text = "It's a tie.."
                winner_color = "gray"
                play_audio("./text-speech/tiegame.mp3")
                wait_for_audio(self)
            
            summary_frame = tk.Frame(self, bg=self.bg_color)
            summary_frame.pack(expand=True, fill=tk.BOTH, padx=50, pady=50)
            final_label = tk.Label(
                master=summary_frame,
                text=winner_text,
                font=font.Font(size=36,weight = "bold"),
                bg = "white",
                fg =winner_color
            )
            final_label.pack(pady=30)
            # SAMI says goodbye
            # self.robot.close_connection()  # Commented out since robot is not initialized

    def _start_next_round(self):

        self.current_round += 1 
       
        self.round_scores = {'player': 0, 'sami': 0, 'draws': 0}
        self._create_widgets()
        self.update_score_display() 
        play_audio(f'./text-speech/{self.current_round}.mp3')
        wait_for_audio(self)
        self.restart_game() # Update round indicator

    def _delayed_restart_game(self):
        self.restart_game()

if __name__ == "__main__":

    game = TicTacToeBoard(default_difficulty="easy")
    game.mainloop()
