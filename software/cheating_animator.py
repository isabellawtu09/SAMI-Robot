
# cheating ideas
# sami distracts player
# move comes out of nowhere
# replace win with samis moves - "dont mind if i do.."


import time
from computer_audio import play_audio, wait_for_audio

class CheatingAnimator:
    def __init__(self, game_instance):
        self.game = game_instance

    def animate_cell_movement(self, target_board):
        self.game.animation_in_progress = True
        self.game.animation_steps = 0
        self.game.display.config(text="Hmm... Hold on a second...")
        play_audio("./text-speech/thinkcheat.mp3")
        wait_for_audio(self.game)

        play_audio("./text-speech/evillaugh.mp3")
        wait_for_audio(self.game)

        current_board = [btn['text'] for btn in self.game.button_identities]
        self.movement_map = {}

        for i, (current_val, target_val) in enumerate(zip(current_board, target_board)):
            if current_val != "" and target_val != "":
                target_idx = target_board.index(current_val)
                if target_idx != i:
                    self.movement_map[i] = {
                        'type': 'move',
                        'from_pos': i,
                        'to_pos': target_idx,
                        'text': current_val,
                        'color': self.game.player_colors.get(current_val, "black")
                    }

        self.animate_piece_movement(target_board)

    def animate_piece_movement(self, target_board):
        if not self.movement_map:
            self.finalize_board_rearrangement(target_board)
            return

        from_pos = list(self.movement_map.keys())[0]
        move_info = self.movement_map[from_pos]
        to_pos = move_info['to_pos']

        def idx_to_coords(idx):
            row = idx // 3
            col = idx % 3
            x = col * 120 + 60
            y = row * 120 + 60
            return x, y

        start_x, start_y = idx_to_coords(from_pos)
        end_x, end_y = idx_to_coords(to_pos)
        steps = 30
        dx = (end_x - start_x) / steps
        dy = (end_y - start_y) / steps

        def move_piece(step):
            if step < steps:
                x = start_x + dx * step
                y = start_y + dy * step
                button = self.game.button_identities[from_pos]
                button.place(x=x, y=y, width=120, height=120)
                self.game.after(16, lambda: move_piece(step + 1))
            else:
                del self.movement_map[from_pos]
                button = self.game.button_identities[from_pos]
                button.place_forget()
                row, col = from_pos // 3, from_pos % 3
                button.grid(row=row, column=col, padx=5, pady=5)
                if self.movement_map:
                    self.animate_piece_movement(target_board)
                else:
                    self.finalize_board_rearrangement(target_board)

        button = self.game.button_identities[from_pos]
        button.grid_remove()
        button.place(x=start_x, y=start_y, width=120, height=120)
        move_piece(0)

    def finalize_board_rearrangement(self, target_board):
        for i, button in enumerate(self.game.button_identities):
            button.place_forget()
            row, col = i // 3, i % 3
            button.grid(row=row, column=col, padx=5, pady=5)
            button.config(
                text=target_board[i],
                bg="#c3c4c7",
                fg=self.game.player_colors.get(target_board[i], "black")
            )
        self.game.buttons_pressed = [i for i, val in enumerate(target_board) if val != ""]

        wins = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],
        [0, 3, 6], [1, 4, 7], [2, 5, 8],
        [0, 4, 8], [2, 4, 6]
        ]
        for a, b, c in wins:
            if target_board[a] == target_board[b] == target_board[c] == "O":
                self.game.highlight_win(a, b, c)
                break
        self.game.samicount += 1
        self.game.round_scores['sami'] += 1
        self.game.update_score_display()
        self.game.display.config(text="I Win! (Fair and square...)")
        play_audio("./text-speech/fairandsquare.mp3")
        wait_for_audio(self.game)
        play_audio("./text-speech/evillaugh.mp3")
        wait_for_audio(self.game)
        self.game.animation_in_progress = False
        self.game.sami_turn_progress = False
        self.game.enable_buttons()
        self.game.after(2000, self.game.play_again)

    def rearrange_board_animation(self, target_board):
        self.animate_cell_movement(target_board)