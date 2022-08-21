from Tetris import Tetris, GoalType, PlacementType
from Tetris import Sounds as TetrisSounds
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
        self.parent.config(bg='black')
        self.white_tetris.music_button.config(command=self.toggle_tetris_music)
        self.black_tetris.music_button.config(command=self.toggle_tetris_music)
        self.parent.after(1, self.start_up)

    def _make_text_label(self, *args):
        return self.white_tetris._make_text_label(*args)

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

    def start_up(self):
        if not self.parent.winfo_ismapped():
            self.parent.wait_visibility()
        start_up_root = tk.Toplevel()
        start_up_root.resizable(0, 0)
        start_up_root.wm_attributes('-type', 'splash')
        start_up_frame = tk.Frame(
            start_up_root,
            bg='black',
            highlightthickness=Tetris.BORDER_WIDTH,
            highlightbackground='white'
        )
        white_ready = tk.BooleanVar(start_up_root, value=False, name='white_ready')
        black_ready = tk.BooleanVar(start_up_root, value=False, name='black_ready')
        ready_text = self._make_text_label(None, 'Ready?', Tetris.UI_FONT_SIZE)
        ready_text2 = self._make_text_label(None, 'Ready.', Tetris.UI_FONT_SIZE)
        ready_text_height = int(self.parent_root.call(ready_text.cget('image'), 'cget', '-height'))
        ready_text_width = int(self.parent_root.call(ready_text.cget('image'), 'cget', '-width'))
        ready_white_button = tk.Button(
            start_up_frame,
            bg='black',
            height=ready_text_height+8,
            width=ready_text_width+8,
            image=ready_text.cget('image'),
            bd=0,
            highlightthickness=Tetris.BORDER_WIDTH,
            highlightbackground='white'
        )
        ready_black_button = tk.Button(
            start_up_frame,
            bg='black',
            height=ready_text_height+8,
            width=ready_text_width+8,
            image=ready_text.cget('image'),
            bd=0,
            highlightthickness=Tetris.BORDER_WIDTH,
            highlightbackground='white'
        )
        white_text = self._make_text_label(start_up_frame, 'White:', Tetris.UI_FONT_SIZE)
        black_text = self._make_text_label(start_up_frame, 'Black:', Tetris.UI_FONT_SIZE)
        countdown = self._make_text_label(start_up_frame, '', Tetris.UI_FONT_SIZE)
        countdowns = ['3', '2', '1', 'GO!']

        def sync_windows(event=None):
            if self.parent.winfo_rootx() != 0:
                start_up_root.update_idletasks()
            start_up_root_x = self.parent.winfo_rootx() + (self.parent.winfo_width() - start_up_root.winfo_width())//2
            start_up_root_y = self.parent.winfo_rooty() + (self.parent.winfo_height() - start_up_root.winfo_height())//2
            start_up_root.geometry(f'+{start_up_root_x}+{start_up_root_y}')

        def display_countdown():
            text = countdowns.pop(0)
            countdown.config(image=self._make_text_label(None, text, Tetris.UI_FONT_SIZE).cget('image'))
            if text == 'GO!':
                self.white_tetris.move_channel.play(TetrisSounds.GO)
            else:
                self.white_tetris.move_channel.play(TetrisSounds.COUNTDOWN)
            if countdowns:
                start_up_root.after(1000, countdown_head)

        def countdown_head(button: tk.Button=None):
            if button is ready_black_button:
                white_ready.set(True)
                button.config(image=ready_text2.cget('image'))
            if button is ready_white_button:
                black_ready.set(True)
                button.config(image=ready_text2.cget('image'))
            if not (white_ready.get() and black_ready.get()):
                return
            if not countdown.winfo_viewable():
                ready_white_button.grid_forget()
                ready_black_button.grid_forget()
                countdown.grid(row=0, column=0)
            display_countdown()
            if not countdowns:
                start_up_root.after(1000, close_and_start)

        def close_and_start():
            self.parent_root.unbind('<Configure>')
            start_up_root.destroy()
            self.white_tetris.play_game()
            self.black_tetris.play_game()

        ready_white_button.config(command=lambda b=ready_white_button: countdown_head(b))
        ready_black_button.config(command=lambda b=ready_black_button: countdown_head(b))
        white_text.grid(row=0, column=0, pady=10, padx=10)
        black_text.grid(row=0, column=1, pady=10, padx=10)
        ready_white_button.grid(row=1, column=0, pady=10, padx=10)
        ready_black_button.grid(row=1, column=1, pady=10, padx=10)
        start_up_frame.update_idletasks()
        start_up_frame.config(
            height=start_up_frame.winfo_reqheight(),
            width=start_up_frame.winfo_reqwidth()
        )
        countdown.config(
            height=start_up_frame.winfo_reqheight()-2*Tetris.BORDER_WIDTH,
            width=start_up_frame.winfo_reqwidth()-2*Tetris.BORDER_WIDTH
        )
        start_up_frame.grid_propagate(False)
        start_up_frame.grid(row=0, column=0)
        start_up_root.transient(self.parent_root)
        sync_windows()
        self.parent_root.bind('<Configure>', sync_windows)


if __name__ == '__main__':
    mixer.pre_init(buffer=4096)
    mixer.init()
    tetris_music = mixer.Channel(0)
    tetris_w_move = mixer.Channel(1)
    tetris_w_line = mixer.Channel(2)
    tetris_b_move = mixer.Channel(3)
    tetris_b_line = mixer.Channel(4)
    chess_sound = mixer.Channel(5)

    root = tk.Tk()
    root.resizable(0, 0)
    root.title('Chesstris')

    chesstris_frame = tk.Frame(root)
    tetris_w_frame = tk.Frame(chesstris_frame)
    tetris_b_frame = tk.Frame(chesstris_frame)
    chess_frame = tk.Frame(chesstris_frame)
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
        allow_play_again=False,
        show_game_over_screen=False
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
        allow_play_again=False,
        show_game_over_screen=False
    )
    chess = Chess(
        parent=chess_frame,
        square_sheet='assets/chess/squares.png',
        sound_channel=chess_sound,
        flip_after_move=False,
        allow_play_again=False,
        show_game_over_screen=False
    )
    chesstris = Chesstris(chesstris_frame, chess, tetris_white, tetris_black)
    tetris_w_frame.grid(row=0, column=0)
    tetris_b_frame.grid(row=0, column=2)
    chess_frame.grid(row=0, column=1)
    chesstris_frame.grid(row=0, column=0)
    root.mainloop()