

import random
import time
#from minimax import Minimax

# Class that will handle the manual input
# given by the user to coordinate with the next
# move by SAMI
# Bugs - 
# Impossible version said " It's a draw " with several spots still available
# Not responsive at times when the game board has already been filled up
# and no one won

class DifficultyManager:
    def __init__(self, game_instance, sami_control = None):
        self.game = game_instance
        self.sami = sami_control
        self.current_difficulty = "normal" # fair

        self.difficulties = {
            "easy" : LoseonPurpose(self),
            "normal" : Fair(self),
            "hard" : Impossible(self)
        }

    def set_difficulties(self, difficulty):
        if difficulty in self.difficulties:
            self.current_difficulty = difficulty
            return True
        return False

    def get_move(self, board):
        difficulty_handler = self.difficulties[self.current_difficulty]
        return difficulty_handler.get_move(board)

    def before_move(self):
        pass # sami does something before placing a move
    def after_move(self):
        pass # sami does something after placing a move

class BaseMode:

    def __init__(self, manager):
        self.manager = manager
        self.game = manager.game
        self.sami = manager.sami
        #self.audio = manager.audio

    def get_available_moves(self, board):
        return [i for i, cell in enumerate(board) if cell == '']

    def check_winner(self, board):
        wins = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # columns
            [0, 4, 8], [2, 4, 6]              # diagonals
        ]
        for a,b,c in wins:
            if board[a] == board[b] == board[c] != '':
                return board[a]
        return None

    def minimax(self, board, depth, is_maximizing, alpha=float('-inf'), beta=float('inf'), difficulty_modifier=1):
        winner = self.check_winner(board)
        if winner == 'O':
            return (10 - depth) * difficulty_modifier
        elif winner == 'X':
            return (-10 + depth) * difficulty_modifier
        elif not self.get_available_moves(board):
            return 0

        if is_maximizing:
            max_eval = float('-inf')
            for move in self.get_available_moves(board):
                board_copy = board.copy()
                board_copy[move] = 'O'
                eval = self.minimax(board_copy, depth + 1, False, alpha, beta, difficulty_modifier)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break  # Prune branch
            return max_eval
        else:
            min_eval = float('inf')
            for move in self.get_available_moves(board):
                board_copy = board.copy()
                board_copy[move] = 'X'
                eval = self.minimax(board_copy, depth + 1, True, alpha, beta, difficulty_modifier)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break  # Prune branch
            return min_eval


    def get_move(self, board):
        raise NotImplementedError
    def pre_move(self):
        pass
    def post_move(self):
        pass

class LoseonPurpose(BaseMode):

    def get_move(self, board):
        # Get next available move and place it there
        available = self.get_available_moves(board)
        if not available:
            return None
        worst_score = float('inf')
        worst_move = None

        for move in available:
            board_copy = board.copy()
            board_copy[move] = 'O'
            score = self.minimax(board_copy, 0, False, difficulty_modifier=0)
            if score < worst_score:
                worst_score = score
                worst_move = move
        # Random moves
        print("SAMI returns the worst move")
        return worst_move

class Fair(BaseMode):
    # 30% chance for robot move to be random, otherwise
    # use the minimax move, i want most games to end in a draw
    def get_move(self, board):
        available = self.get_available_moves(board)
        if not available:
            return None

        best_score = float('-inf')
        best_move = None
        for move in available:
            board_copy = board.copy()
            board_copy[move] = 'O'
            score = self.minimax(board_copy, 0, False, difficulty_modifier=0.7)
            if score > best_score:
                best_score = score
                best_move = move
        if random.random() < 0.2:
            return random.choice(available)
        else:
            return best_move


class Impossible(BaseMode):

    # In this mode - the UI will display various "cheating"
    # behaviors
    # 1 - A cell in which would let SAMI win will show an
    # animation of an X cell moving to that place

    # 2 - Two moves instead of one on SAMI's turn
    # regardless of wether the spot in which it is placed
    # is empty or not, it would be best if this move was placed
    # in a way that then guarantees SAMI's win and not just randomly
    # 3 (maybe?) - "Morph" one of the user's move into a SAMI move
    # It should also be done within a place in the board that is
    # most likely to let SAMI win

    # This mode is bugging out for some reasons
    # It said there was a draw and it seemed to not respond once
    # the board was already full

    def get_move(self, board):
        available = self.get_available_moves(board)
        if not available:
            return None

        best_score = float('-inf')
        best_move = None
        for move in available:
            board_copy = board.copy()
            board_copy[move] = 'O'
            score = self.minimax(board_copy, 0, False, difficulty_modifier=1)
            if score > best_score:
                best_score = score
                best_move = move
        # There is a bigger chance for user to win which means
        # enabling cheating mode so the game therefore becomes
        # "impossible"
        if random.random() < 0.4:
            return random.choice(available)
        else:
            return best_move
        # If SAMI wins - dont add cheat
        # If user manages to win - then -> add cheating behavior

