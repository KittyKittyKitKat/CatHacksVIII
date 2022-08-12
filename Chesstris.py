from Tetris import Tetris, GoalType, PlacementType
from Tetris import Square as TetrisSquare
from Chess import Chess, Team
from Chess import Square as ChessSquare

import tkinter as tk
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
from pygame import mixer

class Chesstris:
    def __init__(self, parent, chess, white_tetris, black_tetris):
        self.parent = parent
        self.chess: Chess = chess
        self.white_tetris: Tetris = white_tetris
        self.black_tetris: Tetris = black_tetris
        self.parent_root = self.parent.winfo_toplevel()
        self.active_game = Tetris
        self.chess.pause_toggle()
        self._set_up_game_event_hooks()
        self.white_tetris.music_button.config(command=self.toggle_tetris_music)
        self.black_tetris.music_button.config(command=self.toggle_tetris_music)

        self.parent_root.bind('<Return>', lambda e: self.swap_games())
        self.parent_root.bind('<space>', lambda e:(self.white_tetris.play_game(), self.black_tetris.play_game(), self.parent_root.unbind('<space>')))

    def _set_up_game_event_hooks(self):
        self.chess.move_listener_flag = tk.StringVar(self.parent, value=self.chess.current_player.name)
        self.move_listener_flag_id = self.chess.move_listener_flag.trace_add('write', self._chess_move_trace)

        self.white_tetris.lines_cleared_flag = tk.IntVar(self.parent, value=-1)
        self.white_lines_cleared_flag_id = self.white_tetris.lines_cleared_flag.trace_add('write', self._white_line_trace)

        self.black_tetris.lines_cleared_flag = tk.IntVar(self.parent, value=-1)
        self.black_lines_cleared_flag_id = self.black_tetris.lines_cleared_flag.trace_add('write', self._black_line_trace)

    def _white_line_trace(self, *args):
        if self.white_tetris.lines_cleared_flag.get() > 0:
            self.chess.change_player(override=Team.WHITE)
            self.swap_games()

    def _black_line_trace(self, *args):
        if self.black_tetris.lines_cleared_flag.get() > 0:
            self.chess.change_player(override=Team.BLACK)
            self.swap_games()

    def _chess_move_trace(self, *args):
        self.swap_games()

    def toggle_tetris_music(self):
        if self.white_tetris.music_channel.get_volume() == 0:
            self.white_tetris.music_button.config(image=self.white_tetris.texts['\U0001D195'])
            self.black_tetris.music_button.config(image=self.black_tetris.texts['\U0001D195'])
            self.white_tetris.music_channel.set_volume(0.1)
        else:
            self.white_tetris.music_channel.set_volume(0)
            self.white_tetris.music_button.config(image=self.white_tetris.texts['\U0001D194'])
            self.black_tetris.music_button.config(image=self.black_tetris.texts['\U0001D194'])

    def swap_games(self):
        self.white_tetris.pause_game()
        self.black_tetris.pause_game()
        self.chess.pause_toggle()


if __name__ == '__main__':
    mixer.pre_init(buffer=4096)
    mixer.init()
    tetris_music = mixer.Channel(0)
    tetris_w_move = mixer.Channel(2)
    tetris_w_line = mixer.Channel(3)
    # tetris_b_music = mixer.Channel(4)
    tetris_b_move = mixer.Channel(5)
    tetris_b_line = mixer.Channel(6)
    chess_sound = mixer.Channel(7)

    root = tk.Tk()
    root.resizable(0, 0)
    root.title('Chesstris')
    root.config(bg='black')

    tetris_w_frame = tk.Frame(root)
    tetris_b_frame = tk.Frame(root)
    chess_frame = tk.Frame(root)
    tetris_w_frame.grid_propagate(False)
    tetris_b_frame.grid_propagate(False)
    chess_frame.grid_propagate(False)

    tetris_w_keys = {
        'soft drop': 's',
        'hard drop': 'w',
        'left': 'a',
        'right': 'd',
        'rotate clockwise': 'x',
        'rotate counterclockwise': 'z',
        'hold': 'c'
    }
    tetris_b_keys = {
        'soft drop': 'Down',
        'hard drop': 'Up',
        'left': 'Left',
        'right': 'Right',
        'rotate clockwise': 'b',
        'rotate counterclockwise': 'n',
        'hold': 'm'
    }

    tetris_white = Tetris(
        parent=tetris_w_frame,
        mirror_ui=True,
        ghost_piece = True,
        placement_mode=PlacementType.EXTENDED,
        starting_level=5,
        goal_type=GoalType.STAGNANT,
        key_mapping=tetris_w_keys,
        allow_pausing=False,
        music_channel=tetris_music,
        move_channel=tetris_w_move,
        line_channel=tetris_w_line,
        start_menu=False,
        allow_play_again=False
    )
    tetris_black = Tetris(
        parent=tetris_b_frame,
        mirror_ui=False,
        ghost_piece = True,
        placement_mode=PlacementType.EXTENDED,
        starting_level=5,
        goal_type=GoalType.STAGNANT,
        key_mapping=tetris_b_keys,
        allow_pausing=False,
        music_channel=tetris_music,
        move_channel=tetris_b_move,
        line_channel=tetris_b_line,
        start_menu=False,
        allow_play_again=False
    )
    chess = Chess(
        parent=chess_frame,
        square_sheet='assets/chess/squares.png',
        sound_channel=chess_sound,
        flip_after_move=False,
        allow_play_again=False
    )
    chesstris = Chesstris(root, chess, tetris_white, tetris_black)
    tetris_w_frame.grid(row=0, column=0)
    tetris_b_frame.grid(row=0, column=2)
    chess_frame.grid(row=0, column=1)
    root.mainloop()