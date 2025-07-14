import tkinter as tk
from tkinter import ttk
from tkinter import font
from tkinter import messagebox
from difficulty_manager import DifficultyManager
import random
from gtts import gTTS
import pygame
import os
import time
from SAMIControl import SAMIControl
# from audio_manager import AudioManager

# TO DO -
#  - dont let user make play again before computer does
#  - audio is acting weird
#  - if first move leads sami to win don't add the second move
#  - change messagebox to something more visible, screen with button
# - use functions from audio manager for audio probability
# - add behaviors depending on conditions and define a baseline " your turn " "my turn " behaviors
# - Keep track of scores from each round to then display at the end of the round
# because of the older population im thinking the round
# could be 3 games for each round ? or 5

# ideas:
# - create messagebox once round is done to prompt user
# to play again instead of having it throughout the entire gameplay
    # - messagebox on tkinter dimensions cant be manipulated
    # might have to change to something else


# states
# 1 - cheating SAMI
# 2 - Non-cheating SAMI
# 3 - SAMI loses on purpose


pygame.mixer.init()

audio_files = {
    "welcome.mp3": "Welcome to Tic-Tac-Toe with SAMI, choose your difficulty level",
    "yourturn.mp3": "Your turn!",
    "myturn.mp3": "My .. turn!",
    "evillaugh.mp3": "mu ah ha ha!",
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


class TicTacToeBoard(tk.Tk):
    # The board's attributes
    def __init__(self, show_menu=True, default_difficulty=None):
        super().__init__()
        self.show_menu = show_menu
        self.play_audio("./text-speech/welcome.mp3")
        self.title("Tic-Tac-Toe")
        self.geometry("600x800")
        self._cells = {}
        self.bg_color = "#9d9fa3"
        self.configure(bg= self.bg_color)
        self.player_colors = {
            "X": "#f59342",
            "O" : "#e0484a"
        }
        self.difficulty_sequence = (
        ["easy"] * 3 +
        ["normal"] * 2 +
        ["hard"] * 2 +
        ["easy"] * 2 +
        ["hard"] * 3
        )
        self.difficulty_seq_index = 0
            # Default beginner is the human user
        self.current_player = "X"
        self.buttons_pressed = []
        self.current_difficulty = None
        self.game_started = False
        # Animation properties
        self.animation_in_progress = False
        self.animation_steps = 0
        self.animation_delay = 90  # milliseconds between animation steps
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
        # # Create connection
        # self.robot.initialize_serial_connection()
        #self._create_widgets()


        self.difficulty_manager = DifficultyManager(
            game_instance = self,
            # sami_control = self.robot,
            #audio_manager = self.audio,
        )
        if show_menu:
            self._mode_selection()
        else:
            self._show_start_button(default_difficulty)
        # self.audio = AudioManager(
        #     starting_voice_type= "DefaultVoice",
        #     audio_folder_path='audio'
        # )

    def _show_start_button(self, default_difficulty):
        for widget in self.winfo_children():
            widget.destroy()
        splash_label = tk.Label(
            master=self,
            text="Welcome to Tic-Tac-Toe with SAMI!",
            font=font.Font(size=40, weight='bold'),
            bg=self.bg_color,
            fg='white'
        )
        splash_label.pack(pady=100)
        start_button = tk.Button(
            master=self,
            text="Start",
            font=font.Font(size=28, weight='bold'),
            width=10,
            height=2,
            command=lambda: self.start_game(default_difficulty if default_difficulty else "easy"),
            bg="#f59342",
            fg="black",
            relief="raised",
            bd=4
        )
        start_button.pack(pady=40)
    def advance_difficulty_sequence(self):
    # Set difficulty from sequence
        if self.difficulty_seq_index < len(self.difficulty_sequence):
            next_diff = self.difficulty_sequence[self.difficulty_seq_index]
            self.set_difficulty(next_diff)
            self.difficulty_seq_index += 1
        else:
            # Optionally, loop or stop at the end
            # For looping:
            self.difficulty_seq_index = 0
            next_diff = self.difficulty_sequence[self.difficulty_seq_index]
            self.set_difficulty(next_diff)
            self.difficulty_seq_index += 1

    # "Animate" cells moving to new positions
    def animate_cell_movement(self, target_board):

        self.animation_in_progress = True
        self.animation_steps = 0
        self.display.config(text="Hmm... Hold on a second...")
        self.play_audio("./text-speech/thinkcheat.mp3")
        self.wait_for_audio()

        # Play evil laugh during change of cells
        self.play_audio("./text-speech/evillaugh.mp3")
        self.wait_for_audio()

        # Calculate movement paths for each piece
        current_board = [btn['text'] for btn in self.button_identities]

        # Create a mapping of what needs to move where
        self.movement_map = {}

        # Find pieces that need to move
        for i, (current_val, target_val) in enumerate(zip(current_board, target_board)):
            if current_val != "" and target_val != "":
                # Find where this piece should end up
                target_idx = target_board.index(current_val)
                if target_idx != i:
                    self.movement_map[i] = {
                        'type': 'move',
                        'from_pos': i,
                        'to_pos': target_idx,
                        'text': current_val,
                        'color': self.player_colors.get(current_val, "black")
                    }

        # Start the movement animation
        self.animate_piece_movement(target_board)

    # Piece animation
    def animate_piece_movement(self, target_board):

        if not self.movement_map:
            # Display that final state of board to give SAMI win
            self.finalize_board_rearrangement(target_board)
            return

        # Get the first piece to animate
        from_pos = list(self.movement_map.keys())[0]
        move_info = self.movement_map[from_pos]
        to_pos = move_info['to_pos']

        # Convert indices to pixel coordinates
        def idx_to_coords(idx):
            row = idx // 3
            col = idx % 3

            x = col * 120 + 60
            y = row * 120 + 60
            return x, y

        start_x, start_y = idx_to_coords(from_pos)
        end_x, end_y = idx_to_coords(to_pos)

        # Animation parameters
        steps = 30
        dx = (end_x - start_x) / steps
        dy = (end_y - start_y) / steps

        def move_piece(step):
            if step < steps:
                x = start_x + dx * step
                y = start_y + dy * step

                # Move the button
                button = self.button_identities[from_pos]
                button.place(x=x, y=y, width=120, height=120)

                # Add some visual effects during movement
                # if step % 4 < 2:
                #     button.config(bg="#ffcccc")
                # else:
                #     button.config(bg="#c3c4c7")

                self.after(16, lambda: move_piece(step + 1))
            else:
                # Animation complete for this piece
                del self.movement_map[from_pos]

                # Reset button position to grid
                button = self.button_identities[from_pos]
                button.place_forget()
                row, col = from_pos // 3, from_pos % 3
                button.grid(row=row, column=col, padx=5, pady=5)

                # Continue with next piece or finish
                if self.movement_map:
                    self.animate_piece_movement(target_board)
                else:
                    self.finalize_board_rearrangement(target_board)

        # Remove from grid and start animation
        button = self.button_identities[from_pos]
        button.grid_remove()
        button.place(x=start_x, y=start_y, width=120, height=120)
        move_piece(0)

    # Move board pieces around
    def rearrange_board_animation(self, target_board):
        self.animate_cell_movement(target_board)

    # Final board state with SAMI as the winner
    def finalize_board_rearrangement(self, target_board):
        # Reset all button positions to their proper grid positions
        for i, button in enumerate(self.button_identities):
            # Make sure button is in grid layout
            button.place_forget()
            row, col = i // 3, i % 3
            button.grid(row=row, column=col, padx=5, pady=5)

            # Update button content to match target board
            button.config(
                text=target_board[i],
                bg="#c3c4c7",
                fg=self.player_colors.get(target_board[i], "black")
            )

        # Update buttons_pressed to reflect new state
        self.buttons_pressed = [i for i, val in enumerate(target_board) if val != ""]

        # SAMI always wins after cheating - no need to check
        self.display.config(text="I Win! (Fair and square...)")
        self.play_audio("./text-speech/fairandsquare.mp3")
        self.wait_for_audio()
        self.play_audio("./text-speech/evillaugh.mp3")
        self.wait_for_audio()
        self.animation_in_progress = False
        self.after(2000, self.play_again)
    # Creates the final state of the board to then show after cheating sequence
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

    # If user happens to win then follow with cheat sequence
    def cheat_after_user_win(self):
        current_board = [btn['text'] for btn in self.button_identities]
        cheating_board = self.create_cheating_board_state(current_board)

        # Start the cheating animation
        self.rearrange_board_animation(cheating_board)
    # Wait for current audio to stop playing before playing the other
    def wait_for_audio(self):
        while pygame.mixer.music.get_busy():
            self.update()
            time.sleep(0.1)
    # Play the given audio file 
    def play_audio(self, filename):
        try:
            if os.path.exists(filename):
                pygame.mixer.music.load(filename)
                pygame.mixer.music.play()
                print("Playing file")
            else:
                print("Not playing file")
        except Exception as e:
            print("Error playing file")
    # User can decide what mode to choose for now
    # before playing the game
    def _mode_selection(self):
        for widget in self.winfo_children():
            widget.destroy()
        welcome_label = tk.Label(
            master=self,
            text = "Welcome to Tic-Tac-Toe with SAMI!",
            font = font.Font(size = 50, weight = 'bold'),
            bg = self.bg_color,
            fg = 'white'
        )
        welcome_label.pack(pady =50)
        instruction_label = tk.Label(
            master = self,
            text = "Choose difficulty level",
            font = font.Font(size= 24),
            bg=self.bg_color,
            fg="white"
        )
        instruction_label.pack(pady=20)
        self.difficulty_frame = tk.Frame(master=self,
                                         bg = self.bg_color)
        self.difficulty_frame.pack(pady=40)

        easy_button = tk.Button(
            master = self.difficulty_frame,
            text = "Easy Peasy",
            font = font.Font(size=20, weight = 'bold'),
            width = 12,
            height = 7,
            command=lambda: self.start_game("easy"),
            bg = "#cbebb0",
            fg = "black",
            relief = "raised",
            bd=4
        )
        easy_button.pack(side=tk.LEFT, padx=30)

        fair_button = tk.Button(
            master = self.difficulty_frame,
            text = "Fair Fight",
            font = font.Font(size=20, weight='bold'),
            width = 12,
            height = 7,
            command=lambda: self.start_game("normal"),
            bg = "#caa2e8",
            fg = "black",
            relief = "raised",
            bd = 4
        )
        fair_button.pack(side=tk.LEFT, padx=30)

        cheat_button = tk.Button(
            master = self.difficulty_frame,
            text = "Impossible!",
            font = font.Font(size = 20, weight = 'bold'),
            width = 12,
            height = 7,
            command=lambda: self.start_game("hard"),
            bg = "#c9446c",
            fg = "black",
            relief = "raised",
            bd = 4
        )

        cheat_button.pack(side=tk.LEFT, padx=30)

    def start_game(self, difficulty):

        self.current_difficulty = difficulty
        self.difficulty_manager.set_difficulties(difficulty)
        self.game_started = True

        for widget in self.winfo_children():
            widget.destroy()

        self._create_widgets()
        # sami acknowledges level chosen


    # Creation of the "button" widgets to
    # place the player's move
    def _create_widgets(self):
        # Creation of title
        self.display = tk.Label(
            master=self,
            text="Your Turn",
            font=font.Font(size=28, weight='bold')
        )
        self.display.pack(pady=20)
        self.after(100, self.play_audio("./text-speech/yourturn.mp3"))
        # self.play_audio("yourturn.mp3")
        # self.wait_for_audio()
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
        #self.robot.start_behavior("Wave.json")
        #self.audio.send_audio('GameIntro_matt')
        #time.sleep(14)
        #self.robot.start_behavior("Home.json")
        # Make sure move is done or stop it before moving on to next move
        # then send it back to home
        # Store empty spaces

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
                    self.play_audio("./text-speech/evillaugh.mp3")
                    self.wait_for_audio()
                    button2.config(text="O", fg=self.player_colors["O"])
                    self.buttons_pressed.append(s2ndmove)
            # If this move led to the human winning and the difficulty level
            # is in hard then call cheating function on the move just made that lead to the win
            # or make 2 moves but this would be before this ?

        # Check board state before continuing game
        winner = self.check_winner()
        if winner:
            # My/your turn instead of player {} turn for less confusion?
            self.display.config(text= f"I win!")
            self.play_audio("./text-speech/samiwin.mp3")
            self.wait_for_audio()
            # self.robot.start_behavior("Home.json")
            # Delays
            self.after(1000, self.play_again)
        elif all(btn['text'] != '' for btn in self.button_identities):
            if self.current_difficulty == "hard":
                self.display.config(text = "It's a Draw!.. or is it?")
                self.play_audio("./text-speech/draw.mp3")
                self.wait_for_audio()
                self.after(2000, self.cheat_after_user_win)
                return
            self.display.config(text = "It's a Draw!")
            self.play_audio("./text-speech/normaldraw.mp3")
            self.wait_for_audio()
            # self.robot.start_behavior("Home.json")
            self.after(1000, self.play_again)
        else:
            # Return back to human player if no one has won
            # Return back to human player if no one has won

            # Play "Your turn" audio AFTER SAMI's move
            self.display.config(text="Your Turn")
            self.current_player = "X"
            self.play_audio("./text-speech/yourturn.mp3")
            self.wait_for_audio()  # Let it finish before giving control

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
        if not self.game_started or self.animation_in_progress:
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
                    self.play_audio("./text-speech/cheatwin.mp3")
                    self.wait_for_audio()
                    self.after(2000, self.cheat_after_user_win)
                    return
                self.display.config(text=f"You Win!")
                self.play_audio("./text-speech/win.mp3")
                self.wait_for_audio()
                self.after(1000, self.play_again)
            elif winner == "O":
                self.display.config(text=f"I Win!")
                self.play_audio("./text-speech/samiwin.mp3")
                self.wait_for_audio()
                self.after(1000, self.play_again)
            elif all(btn['text'] != '' for btn in self.button_identities):
                if self.current_difficulty == "hard":
                    self.display.config(text = "It's a Draw!.. or is it?")
                    self.play_audio("./text-speech/draw.mp3")
                    self.wait_for_audio()
                    self.after(2000, self.cheat_after_user_win)
                    return
                self.display.config(text="It's a Draw!")
                self.after(1000, self.play_again)
            else:
                # Play "My turn" audio BEFORE SAMI's move
                self.display.config(text=f"My Turn")
                self.current_player = "O"
                # Delay before making the robot's move
                self.play_audio("./text-speech/myturn.mp3")
                self.wait_for_audio()  # Let audio finish
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
        self.display.config(text="Your Turn")
        self.play_audio("./text-speech/yourturn.mp3")
        self.wait_for_audio()

    def set_difficulty(self, new_difficulty):
        if self.current_difficulty != new_difficulty:
            self.current_difficulty = new_difficulty
            self.difficulty_manager.set_difficulties(new_difficulty)
            # Optional: give feedback in the UI
            if hasattr(self, 'display'):
                self.display.config(text=f"Difficulty changed to {new_difficulty.capitalize()}")

    def play_again(self):
        self.after(1000)
        self.play_audio("./text-speech/playagain.mp3")
        result = tk.messagebox.askquestion(title=None, message="Play with me again?", type = "yesno")

        # Restart the game and clear any highlighted cells etc.
        if result == "yes":
            if not self.show_menu:
                self.advance_difficulty_sequence()
            self.restart_game()
        else:
        # Prompt user with mode again
            if not self.show_menu:
                pass 
            self._mode_selection()



# Start game
if __name__ == "__main__":
    # To show menu: game = TicTacToeBoard()
    # To skip menu and start on easy: game = TicTacToeBoard(show_menu=False, default_difficulty="easy")
    game = TicTacToeBoard(show_menu = True, default_difficulty="easy")
    game.mainloop()
    # close connection here with the SAMIControl function