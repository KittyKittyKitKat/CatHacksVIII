from Chess import Chess, Team
from Tetris import Tetris

import tkinter as tk
from time import sleep

class Chesstris:
    def __init__(self, root_win, p1tetris, p2tetris, chess):
        self.root = root_win
        self.p1tetris = p1tetris
        self.p2tetris = p2tetris
        self.chess = chess
        self.run_tetris = True
        self.player_chess_move = None

    def create_games(self):
        self.p1tetris.set_up_board()
        # self.root.bind('s', lambda event: self.p1tetris.tetromino_fall())
        self.root.bind('a', lambda event: self.p1tetris.tetromino_left())
        self.root.bind('d', lambda event: self.p1tetris.tetromino_right())
        self.root.bind('z', lambda event: self.p1tetris.tetromino_rotate('ccw'))
        self.root.bind('x', lambda event: self.p1tetris.tetromino_rotate('cw'))

        self.p2tetris.set_up_board()
        # self.root.bind('<Down>', lambda event: self.p2tetris.tetromino_fall())
        self.root.bind('<Left>', lambda event: self.p2tetris.tetromino_left())
        self.root.bind('<Right>', lambda event: self.p2tetris.tetromino_right())
        self.root.bind('.', lambda event: self.p2tetris.tetromino_rotate('ccw'))
        self.root.bind('/', lambda event: self.p2tetris.tetromino_rotate('cw'))

        self.chess.set_up_board()
        self.chess.create_classic_setup()
        self.chess.locked = True

    def spawn_tetris_pieces(self):
        self.p1tetris.random_tetromino()
        self.p2tetris.random_tetromino()

    def lock_tetris(self):
        self.run_tetris = False
        self.root.unbind('s')
        self.root.unbind('a')
        self.root.unbind('d')
        self.root.unbind('z')
        self.root.unbind('x')

        self.root.unbind('<Down>')
        self.root.unbind('<Left>')
        self.root.unbind('<Right>')
        self.root.unbind('.')
        self.root.unbind('/')

    def unlock_tetris(self):
        self.run_tetris = True
        # self.root.bind('s', lambda event: self.p1tetris.tetromino_fall())
        self.root.bind('a', lambda event: self.p1tetris.tetromino_left())
        self.root.bind('d', lambda event: self.p1tetris.tetromino_right())
        self.root.bind('z', lambda event: self.p1tetris.tetromino_rotate('ccw'))
        self.root.bind('x', lambda event: self.p1tetris.tetromino_rotate('cw'))

        # self.root.bind('<Down>', lambda event: self.p2tetris.tetromino_fall())
        self.root.bind('<Left>', lambda event: self.p2tetris.tetromino_left())
        self.root.bind('<Right>', lambda event: self.p2tetris.tetromino_right())
        self.root.bind('.', lambda event: self.p2tetris.tetromino_rotate('ccw'))
        self.root.bind('/', lambda event: self.p2tetris.tetromino_rotate('cw'))

    def play_chess(self):
        self.chess.locked = False
        self.chess.current_player = self.player_chess_move


if __name__ == '__main__':
    root = tk.Tk()
    root.resizable(0, 0)
    root.title('Chesstris')
    root.config(bg='#333')
    p1frame = tk.Frame(root, height=Tetris.SQUARE_SIZE*Tetris.ROWS, width=Tetris.SQUARE_SIZE*Tetris.COLUMNS)
    p2frame = tk.Frame(root, height=Tetris.SQUARE_SIZE*Tetris.ROWS, width=Tetris.SQUARE_SIZE*Tetris.COLUMNS)
    chessframe = tk.Frame(root, height=Chess.SQUARE_SIZE*Chess.RANKS, width=Chess.SQUARE_SIZE*Chess.FILES)
    p1frame.grid_propagate(False)
    p2frame.grid_propagate(False)
    chessframe.grid_propagate(False)
    player_1_tetris = Tetris(p1frame)
    player_2_tetris = Tetris(p2frame)
    chess = Chess(chessframe)
    p1frame.grid(row=0, column=0)
    p2frame.grid(row=0, column=2)
    chessframe.grid(row=0, column=1)
    chesstris = Chesstris(root, player_1_tetris, player_2_tetris, chess)
    chesstris.create_games()
    game_time = 0
    while True:
        try:
            root.update_idletasks()
            root.update()
            sleep(0.01)
            game_time += 1
            if not chesstris.chess.locked:
                if chesstris.chess.move_made == 'Success':
                    chesstris.chess.locked = True
                    chesstris.chess.move_made = None
                    chesstris.unlock_tetris()
            if game_time == 30:
                game_time = 0
                if chesstris.run_tetris:
                    chesstris.spawn_tetris_pieces()
                    p1_line_cleared = chesstris.p1tetris.tetromino_fall()
                    p2_line_cleared = chesstris.p2tetris.tetromino_fall()
                    if p1_line_cleared:
                        chesstris.player_chess_move = Team.WHITE
                        chesstris.lock_tetris()
                        chesstris.play_chess()
                    if p2_line_cleared:
                        chesstris.player_chess_move = Team.BLACK
                        chesstris.lock_tetris()
                        chesstris.play_chess()
        except tk.TclError:
            break

