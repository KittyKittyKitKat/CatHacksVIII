import tkinter as tk
import time
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
from pygame import mixer
from enum import Enum, auto
from random import shuffle, randint
from PIL import Image, ImageDraw, ImageFont, ImageTk


def rotate_matrix(matrix, clockwise):
    transpose = [
        [matrix[j][i] for j in range(len(matrix))]
        for i in range(len(matrix[0]))
    ]
    if clockwise:
        return [row[::-1] for row in transpose]
    else:
        return transpose[::-1]


class PlacementType(Enum):
    EXTENDED = auto()
    INFINITE = auto()
    CLASSIC = auto()


class GoalType(Enum):
    FIXED = auto()
    VARIABLE = auto()


class TetriminoImage(Enum):
    I = Image.open('assets/tetris/sprites/cyan.png')
    J = Image.open('assets/tetris/sprites/blue.png')
    L = Image.open('assets/tetris/sprites/orange.png')
    O = Image.open('assets/tetris/sprites/yellow.png')
    T = Image.open('assets/tetris/sprites/purple.png')
    S = Image.open('assets/tetris/sprites/green.png')
    Z = Image.open('assets/tetris/sprites/red.png')
    GHOST = Image.open('assets/tetris/sprites/ghost.png')
    GARBAGE = Image.open('assets/tetris/sprites/garbage.png')


class TetriminoType(Enum):
    I = [[0, 0, 0, 0],
        [1, 1, 1, 1],
        [0, 0, 0, 0],
        [0, 0, 0, 0]]
    J = [[1, 0, 0],
        [1, 1, 1],
        [0, 0, 0]]
    L = [[0, 0, 1],
        [1, 1, 1],
        [0, 0, 0]]
    O = [[1, 1],
        [1, 1]]
    T = [[0, 1, 0],
        [1, 1, 1],
        [0, 0, 0]]
    S = [[0, 1, 1],
        [1, 1, 0],
        [0, 0, 0]]
    Z = [[1, 1, 0],
        [0, 1, 1],
        [0, 0, 0]]


class RotationState(Enum):
    NORTH = auto()
    EAST = auto()
    SOUTH = auto()
    WEST = auto()

    @classmethod
    def get_next_rotation_state(cls, starting_rotation, clockwise):
        new_rotation_state = None
        if clockwise:
            match starting_rotation:
                case RotationState.NORTH:
                    new_rotation_state = RotationState.EAST
                case RotationState.EAST:
                    new_rotation_state = RotationState.SOUTH
                case RotationState.SOUTH:
                    new_rotation_state = RotationState.WEST
                case RotationState.WEST:
                    new_rotation_state = RotationState.NORTH
        else:
            match starting_rotation:
                case RotationState.NORTH:
                    new_rotation_state = RotationState.WEST
                case RotationState.EAST:
                    new_rotation_state = RotationState.NORTH
                case RotationState.SOUTH:
                    new_rotation_state = RotationState.EAST
                case RotationState.WEST:
                    new_rotation_state = RotationState.SOUTH
        return new_rotation_state


class Sounds:
    KOROBEINIKI = 'assets/tetris/audio/korobeiniki.wav'
    MOVE = 'assets/tetris/audio/move.wav'
    LOCK = 'assets/tetris/audio/lock.wav'
    GAME_OVER = 'assets/tetris/audio/game_over.wav'
    COUNTDOWN = 'assets/tetris/audio/countdown.wav'
    GO = 'assets/tetris/audio/go.wav'
    HOLD = 'assets/tetris/audio/hold.wav'
    CLEAR = 'assets/tetris/audio/clear.wav'
    TETRIS = 'assets/tetris/audio/tetris.wav'
    HIGH_ALERT = 'assets/tetris/audio/high_alert.wav'
    LOW_ALERT = 'assets/tetris/audio/low_alert.wav'

    def __getattribute__(self, name):
        return mixer.Sound(file=super(type(Sounds), self).__getattribute__(name))
Sounds = Sounds()

class Mino:
    def __init__(self, image, placed):
        self.image = image
        self.placed = placed


class Tetrimino:
    def __init__(self, piece_type, upper_left_coords, ghost=False):
        self.piece_type = piece_type
        self.upper_left_coords = upper_left_coords
        self.ghost = ghost
        self.placed = False
        self.rotation_state = RotationState.NORTH
        if self.ghost:
            mino_image = TetriminoImage.GHOST.value
        else:
            mino_image = TetriminoImage[piece_type.name].value
        self.minos = [
            [
                Mino(mino_image, False)
                if col == 1 else None for col in row
            ]
            for row in self.piece_type.value
        ]

    def get_wall_kick_tests(self, next_rotation):
        current_rotation = self.rotation_state
        kicks = []
        match (current_rotation, next_rotation):
            case RotationState.NORTH, RotationState.EAST:
                if self.piece_type is TetriminoType.I:
                    kicks =  [(-2, 0), (1, 0), (-2, 1), (1, -2)]
                else:
                    kicks =  [(-1, 0), (-1, -1), (0, 2), (-1, 2)]
            case RotationState.EAST, RotationState.NORTH:
                if self.piece_type is TetriminoType.I:
                    kicks =  [(2, 0), (-1, 0), (2, -1), (-1, 2)]
                else:
                    kicks =  [(1, 0), (1, 1), (0, -2), (1, -2)]
            case RotationState.EAST, RotationState.SOUTH:
                if self.piece_type is TetriminoType.I:
                    kicks =  [(-1, 0), (2, 0), (-1, -2), (2, 1)]
                else:
                    kicks =  [(1, 0), (1, 1), (0, -2), (1, -2)]
            case RotationState.SOUTH, RotationState.EAST:
                if self.piece_type is TetriminoType.I:
                    kicks =  [(1, 0), (-2, 0), (1, 2), (-2, -1)]
                else:
                    kicks =  [(-1, 0), (-1, -1), (0, 2), (-1, 2)]
            case RotationState.SOUTH, RotationState.WEST:
                if self.piece_type is TetriminoType.I:
                    kicks =  [(2, 0), (-1, 0), (2, -1), (-1, 2)]
                else:
                    kicks =  [(1, 0), (1, -1), (0, 2), (1, 2)]
            case RotationState.WEST, RotationState.SOUTH:
                if self.piece_type is TetriminoType.I:
                    kicks =  [(-2, 0), (1, 0), (-2, 1), (1, -2)]
                else:
                    kicks =  [(-1, 0), (-1, 1), (0, -2), (-1, -2)]
            case RotationState.WEST, RotationState.NORTH:
                if self.piece_type is TetriminoType.I:
                    kicks =  [(1, 0), (-2, 0), (1, 2), (-2, -1)]
                else:
                    kicks =  [(-1, 0), (-1, 1), (0, -2), (-1, -2)]
            case RotationState.NORTH, RotationState.WEST:
                if self.piece_type is TetriminoType.I:
                    kicks =  [(-1, 0), (2, 0), (-1, -2), (2, 1)]
                else:
                    kicks =  [(1, 0), (1, -1), (0, 2), (1, 2)]
        kicks.insert(0, (0, 0))
        return kicks

    def get_mino_coords(self, row_offset=0, col_offset=0):
        start_x, start_y = self.upper_left_coords
        x, y = start_x, start_y
        mino_coords = []
        for row in self.minos:
            for mino in row:
                if isinstance(mino, Mino):
                    mino_coords.append((y+row_offset, x+col_offset, mino))
                x += 1
            x = start_x
            y +=1
        return mino_coords

    def get_corner_coords(self):
        size = len(self.piece_type.value)
        y, x = self.upper_left_coords
        lx, ly = x + size - 1, y + size - 1
        coords = [
            [(x, y),
            (x, ly)],
            [(lx, y),
            (lx, ly)]
        ]
        return coords

    def place(self):
        self.placed = True
        for row in self.minos:
            for mino in row:
                if isinstance(mino, Mino):
                    mino.placed = True

    def rotate(self, clockwise):
        self.minos = rotate_matrix(self.minos, clockwise)
        self.rotation_state = RotationState.get_next_rotation_state(self.rotation_state, clockwise)

    def move_horizontally(self, dir, amount):
        x, y = self.upper_left_coords
        self.upper_left_coords = x + (dir * amount), y

    def move_vertically(self, dir, amount):
        x, y = self.upper_left_coords
        self.upper_left_coords = x, y + (dir * amount)

    def __repr__(self):
        return f'{self.piece_type.name} Tetrimino. Placed={self.placed}. Coords={self.upper_left_coords}. Ghost={self.ghost}'

    def __str__(self):
        string = ''
        for row in self.minos:
            for mino in row:
                if isinstance(mino, Mino):
                    string += '\u25A0'
                else:
                    string += ' '
            string += '\n'
        return string[:-1]


class Square(tk.Label):
    SQUARE_SIZE = 32

    def __init__(self, parent, background_image):
        self.parent = parent
        self.mino = None
        self.background_image = background_image
        self.tk_image = ImageTk.PhotoImage(self.background_image)
        super().__init__(parent, width=Square.SQUARE_SIZE, height=Square.SQUARE_SIZE, bg='black', bd=0, image=self.tk_image)

    def place_mino(self, mino):
        self.mino = mino
        piece_image = mino.image
        composite = ImageTk.getimage(self.tk_image).copy()
        composite.paste(piece_image, (0, 0), piece_image)
        self.tk_image = ImageTk.PhotoImage(composite)
        self.config(image=self.tk_image)

    def remove_mino(self):
        self.mino = None
        self.tk_image = ImageTk.PhotoImage(self.background_image)
        self.config(image=self.tk_image)


class Tetris:
    ROWS = 20
    COLUMNS = 10
    BUFFER_ROWS = 20
    HOLD_ROWS = 4
    NEXT_ROWS =  18
    NEXT_PIECES = 6
    UI_COLUMNS = 4
    GARBAGE_COLUMNS = 1
    UI_FONT_SIZE = 20
    BORDER_WIDTH = 2
    UI_INNER_PADDING = 6
    TOTAL_HEIGHT = 24
    SKYLINE_VISIBILITY = 8
    MAX_LEVEL = 15

    def __init__(self,
                 parent,
                 mirror_ui,
                 ghost_piece,
                 placement_mode,
                 starting_level,
                 goal_type,
                 key_mapping,
                 allow_pausing,
                 music_channel,
                 move_channel,
                 line_channel,
                 start_menu,
                 allow_play_again
        ):
        self.parent = parent
        self.mirror_ui = mirror_ui
        self.ghost_piece = ghost_piece
        self.placement_mode = placement_mode
        self.starting_level = starting_level
        self.goal_type = goal_type
        self.key_mapping = key_mapping
        self.allow_pausing = allow_pausing
        self.music_channel = music_channel
        self.move_channel = move_channel
        self.line_channel = line_channel
        self.start_menu = start_menu
        self.allow_play_again = allow_play_again
        self.parent_root = self.parent.winfo_toplevel()
        self.game_frame = tk.Frame(self.parent)
        self.ui_frame = tk.Frame(self.parent)
        self.next_frame = tk.Frame(self.parent)
        self.hold_frame = tk.Frame(self.parent)
        self.score_frame = tk.Frame(self.parent)
        self.garbage_frame = tk.Frame(self.parent)
        self.score_label = tk.Label(self.score_frame)
        self.lines_label = tk.Label(self.score_frame)
        self.level_label = tk.Label(self.score_frame)
        self.goal_label = tk.Label(self.score_frame)
        self.pause_button = tk.Button(self.score_frame)
        self.music_button = tk.Button(self.score_frame)
        self.sound_button = tk.Button(self.score_frame)
        self.texts = {}
        self.lock_time = 500
        self.game_started = False
        self.falling_lowest = 0
        self.level = self.starting_level
        self.score = 0
        self.back_to_back = False
        self.lines_cleared = 0
        self.goal = self.get_next_goal()
        self.play_id = None
        self.lock_moves = tk.IntVar(master=self.parent, value=15)
        self.lock_movement = False
        self.lock_id = None
        self.lock_engaged = False
        self.auto_repeat = ''
        self.key_time = 0
        self.speed_factor = 1
        self.rotation_point = None
        self.falling_tetrimino = None
        self.held_tetrimino = None
        self.ghost_tetrimino = None
        self.game_paused = False
        self.game_over = tk.BooleanVar(master=self.parent, value=False)
        self.has_held = False
        self.queued_garbage = 0
        self.next_tetriminos = []
        self.seven_bag = []
        self.playfield = []
        self.next_area = []
        self.hold_area = []
        self.garbage_area = []
        self.empty_image = Image.new('RGBA', (Square.SQUARE_SIZE, Square.SQUARE_SIZE), (0, 0, 0))
        self._config_widgets()
        self._set_up_playfield()
        self._set_up_next_area()
        self._set_up_hold_area()
        self._set_up_score_area()
        self._set_up_garbage_area()
        self._set_up_keybindings()
        self.show_score()
        self.show_lines()
        self.show_level()
        self.show_goal()
        self.lock_trace_id = self.lock_moves.trace_add('write', self._lock_trace)
        self.game_over_trace_id = self.game_over.trace_add('write', self._game_over_trace)
        self.music_channel.set_volume(0.1)
        self.move_channel.set_volume(0.4)
        self.line_channel.set_volume(0.3)
        if self.start_menu:
            self.start_up()

    def _config_widgets(self):
        self.parent.config(
            bg='black',
            height=Square.SQUARE_SIZE*Tetris.TOTAL_HEIGHT+2*Tetris.BORDER_WIDTH+Tetris.SKYLINE_VISIBILITY,
            width=Square.SQUARE_SIZE*(Tetris.COLUMNS+Tetris.UI_COLUMNS+Tetris.GARBAGE_COLUMNS)+6*Tetris.BORDER_WIDTH+2*Tetris.UI_INNER_PADDING,
        )
        self.game_frame.config(
            bg='black',
            height=Tetris.ROWS*Square.SQUARE_SIZE+2*Tetris.BORDER_WIDTH+Tetris.SKYLINE_VISIBILITY,
            width=Tetris.COLUMNS*Square.SQUARE_SIZE+2*Tetris.BORDER_WIDTH,
            highlightbackground='white',
            highlightthickness=Tetris.BORDER_WIDTH
        )
        self.ui_frame.config(
            bg='black',
            width=Tetris.UI_COLUMNS*Square.SQUARE_SIZE+2*(Tetris.BORDER_WIDTH + Tetris.UI_INNER_PADDING),
            height=Square.SQUARE_SIZE*Tetris.ROWS+2*Tetris.BORDER_WIDTH+Tetris.SKYLINE_VISIBILITY,
            highlightbackground='white',
            highlightthickness=Tetris.BORDER_WIDTH
        )
        self.next_frame.config(
            bg='black',
            width=Tetris.UI_COLUMNS*Square.SQUARE_SIZE + 2 * (Tetris.BORDER_WIDTH + Tetris.UI_INNER_PADDING),
            height=Tetris.NEXT_ROWS*Square.SQUARE_SIZE + 2 * Tetris.BORDER_WIDTH,
            highlightbackground='white',
            highlightthickness=Tetris.BORDER_WIDTH
        )
        self.hold_frame.config(
            bg='black',
            width=Tetris.UI_COLUMNS*Square.SQUARE_SIZE + 2 * (Tetris.BORDER_WIDTH + Tetris.UI_INNER_PADDING),
            height=Tetris.HOLD_ROWS*Square.SQUARE_SIZE + 2 * Tetris.BORDER_WIDTH,
            highlightbackground='white',
            highlightthickness=Tetris.BORDER_WIDTH
        )
        self.score_frame.config(
            bg='black',
            width=Square.SQUARE_SIZE*Tetris.COLUMNS+2*Tetris.BORDER_WIDTH,
            height=Square.SQUARE_SIZE*(Tetris.TOTAL_HEIGHT-Tetris.ROWS),
            highlightbackground='white',
            highlightthickness=Tetris.BORDER_WIDTH
        )
        self.garbage_frame.config(
            bg='black',
            width=Square.SQUARE_SIZE*Tetris.GARBAGE_COLUMNS+2*Tetris.BORDER_WIDTH,
            height=Square.SQUARE_SIZE*Tetris.TOTAL_HEIGHT+2*Tetris.BORDER_WIDTH+Tetris.SKYLINE_VISIBILITY,
            highlightbackground='white',
            highlightthickness=Tetris.BORDER_WIDTH
        )
        self.score_label.config(
            bg='black',
            bd=0
        )
        self.lines_label.config(
            bg='black',
            bd=0
        )
        self.level_label.config(
            bg='black',
            bd=0
        )
        self.goal_label.config(
            bg='black',
            bd=0
        )
        self.pause_button.config(
            bg='black',
            bd=0,
            highlightthickness=Tetris.BORDER_WIDTH,
            activebackground='black',
            height=2*Square.SQUARE_SIZE//3,
            width=2*Square.SQUARE_SIZE//3,
        )
        self.sound_button.config(
            bg='black',
            bd=0,
            highlightthickness=Tetris.BORDER_WIDTH,
            activebackground='black',
            height=2*Square.SQUARE_SIZE//3,
            width=2*Square.SQUARE_SIZE//3,
        )
        self.music_button.config(
            bg='black',
            bd=0,
            highlightthickness=Tetris.BORDER_WIDTH,
            activebackground='black',
            height=2*Square.SQUARE_SIZE//3,
            width=2*Square.SQUARE_SIZE//3,
        )

        self.parent.grid_propagate(False)
        self.game_frame.grid_propagate(False)
        self.next_frame.grid_propagate(False)
        self.hold_frame.grid_propagate(False)
        self.score_frame.grid_propagate(False)
        self.garbage_frame.grid_propagate(False)
        self.next_frame.columnconfigure(0, weight=1)
        self.next_frame.columnconfigure(4, weight=1)
        self.hold_frame.columnconfigure(0, weight=1)
        self.hold_frame.columnconfigure(4, weight=1)
        size = self._make_text_label(None, '0'*7, Tetris.UI_FONT_SIZE)
        size = int(self.parent_root.call(size.cget('image'), 'cget', '-width'))
        self.score_frame.columnconfigure(1, minsize=size)
        self.score_frame.columnconfigure(2, weight=1)
        self.game_frame.rowconfigure(0, weight=1)

    def _set_up_playfield(self):
        for row in range(Tetris.ROWS+Tetris.BUFFER_ROWS):
            well_row = []
            for col in range(Tetris.COLUMNS):
                square = Square(self.game_frame, self.empty_image)
                if row >= Tetris.BUFFER_ROWS-1:
                    square.grid(row=row-Tetris.ROWS+1, column=col, sticky=tk.N)
                well_row.append(square)
            self.playfield.append(well_row)
        self.game_frame.grid(row=0, column=1, rowspan=4)
        self.ui_frame.grid(row=0, column=int(not self.mirror_ui)*2, rowspan=4)

    def _set_up_next_area(self):
        for row in range(Tetris.NEXT_ROWS):
            well_row = []
            for col in range(Tetris.UI_COLUMNS):
                square = Square(self.next_frame, self.empty_image)
                square.grid(row=row, column=col+1, sticky=tk.W)
                well_row.append(square)
            self.next_area.append(well_row)
        self.next_frame.grid(row=3, column=int(not self.mirror_ui)*2, rowspan=2)
        next_label = self._make_text_label(self.parent, 'NEXT', Tetris.UI_FONT_SIZE)
        next_label.grid(row=2, column=int(not self.mirror_ui)*2, sticky=tk.NS)

    def _set_up_hold_area(self):
        for row in range(Tetris.HOLD_ROWS):
            well_row = []
            for col in range(Tetris.UI_COLUMNS):
                square = Square(self.hold_frame, self.empty_image)
                square.grid(row=row, column=col+1, sticky=tk.W)
                well_row.append(square)
            self.hold_area.append(well_row)
        self.hold_frame.grid(row=1, column=int(not self.mirror_ui)*2, sticky=tk.NS)
        hold_label = self._make_text_label(self.parent, 'HOLD', Tetris.UI_FONT_SIZE)
        hold_label.grid(row=0, column=int(not self.mirror_ui)*2)

    def _set_up_score_area(self):
        score_text = self._make_text_label(self.score_frame, 'SCORE:', Tetris.UI_FONT_SIZE)
        lines_text = self._make_text_label(self.score_frame, 'LINES:', Tetris.UI_FONT_SIZE)
        level_text = self._make_text_label(self.score_frame, 'LEVEL:', Tetris.UI_FONT_SIZE)
        goal_text = self._make_text_label(self.score_frame, 'GOAL:', Tetris.UI_FONT_SIZE)
        self._make_text_label(self.score_frame, '\u23f8', int(Tetris.UI_FONT_SIZE*1.5), symbol=True)
        self._make_text_label(self.score_frame, '\u23f5', int(Tetris.UI_FONT_SIZE*1.5), symbol=True)
        self._make_text_label(self.score_frame, '\U0001D195', int(Tetris.UI_FONT_SIZE*3), symbol=True)
        self._make_text_label(self.score_frame, '\U0001D194', int(Tetris.UI_FONT_SIZE*3), symbol=True)
        self._make_text_label(self.score_frame, '\U0001F507', Tetris.UI_FONT_SIZE, symbol=True)
        self._make_text_label(self.score_frame, '\U0001F50A', Tetris.UI_FONT_SIZE, symbol=True)

        score_text.grid(
            row=0,
            column=0,
            sticky=tk.W,
            padx=Tetris.UI_INNER_PADDING,
            pady=Tetris.UI_INNER_PADDING
        )
        lines_text.grid(
            row=1,
            column=0,
            sticky=tk.W,
            padx=Tetris.UI_INNER_PADDING,
            pady=Tetris.UI_INNER_PADDING
        )
        level_text.grid(
            row=3,
            column=0,
            sticky=tk.W,
            padx=Tetris.UI_INNER_PADDING,
            pady=Tetris.UI_INNER_PADDING
        )
        goal_text.grid(
            row=4,
            column=0,
            sticky=tk.W,
            padx=Tetris.UI_INNER_PADDING,
            pady=Tetris.UI_INNER_PADDING
        )
        self.pause_button.config(image=self.texts['\u23f8'], command=self.pause_game)
        self.music_button.config(image=self.texts['\U0001D195'], command=self.music_toggle)
        self.sound_button.config(image=self.texts['\U0001F50A'], command=self.sound_toggle)
        self.score_label.grid(row=0, column=1, sticky=tk.W)
        self.lines_label.grid(row=1, column=1, sticky=tk.W)
        self.level_label.grid(row=3, column=1, sticky=tk.W)
        self.goal_label.grid(row=4, column=1, sticky=tk.W)

        if self.allow_pausing:
            self.pause_button.grid(row=0, column=3, rowspan=1, sticky=tk.E, padx=Tetris.UI_INNER_PADDING, pady=(Tetris.UI_INNER_PADDING, 0))
        self.music_button.grid(row=1, column=3, rowspan=3, sticky=tk.E, padx=Tetris.UI_INNER_PADDING, pady=Tetris.UI_INNER_PADDING)
        self.sound_button.grid(row=4, column=3, rowspan=1, sticky=tk.E, padx=Tetris.UI_INNER_PADDING, pady=(0, Tetris.UI_INNER_PADDING))

        self.score_frame.grid(row=4, column=1)

    def _set_up_garbage_area(self):
        for i in range(Tetris.TOTAL_HEIGHT):
            square = Square(self.garbage_frame, self.empty_image)
            square.grid(row=i+1, column=0, sticky=tk.S)
            self.garbage_area.append([square])
        self.garbage_frame.grid_rowconfigure(0, minsize=Tetris.SKYLINE_VISIBILITY)
        self.garbage_frame.grid(row=0, column=int(self.mirror_ui)*2, rowspan=5)

    def _set_up_keybindings(self):
        valid_binding_names = [
            'soft drop',
            'hard drop',
            'left',
            'right',
            'rotate clockwise',
            'rotate counterclockwise',
            'hold'
        ]
        for key in self.key_mapping:
            if key not in valid_binding_names:
                raise KeyError(
                    f'Invalid keybinding name: {key}. Must be one of: {", ".join(valid_binding_names)}'
                )
        self.parent_root.bind('<KeyPress>', self._keypress_dispatch, add='+')
        self.parent_root.bind('<KeyRelease>', self._keyrelease_dispatch, add='+')

    def _uncover_playfield(self):
        for row in range(Tetris.ROWS+Tetris.BUFFER_ROWS):
            for col in range(Tetris.COLUMNS):
                square = self.playfield[row][col]

                if row >= Tetris.BUFFER_ROWS-1:
                    if not square.winfo_ismapped():
                        square.grid(row=row-Tetris.ROWS+1, column=col, sticky=tk.N)

    def _uncover_next_area(self):
        for row in range(Tetris.NEXT_ROWS):
            for col in range(Tetris.UI_COLUMNS):
                square = self.next_area[row][col]
                if not square.winfo_ismapped():
                    square.grid(row=row, column=col+1, sticky=tk.W)

    def _uncover_hold_area(self):
        for row in range(Tetris.HOLD_ROWS):
            for col in range(Tetris.UI_COLUMNS):
                square = self.hold_area[row][col]
                if not square.winfo_ismapped():
                    square.grid(row=row, column=col+1, sticky=tk.W)

    def _keypress_dispatch(self, event):
        if self.game_over.get() or self.game_paused:
            return
        if time.time() - self.key_time > .01:
            self.auto_repeat = ''
        key = event.keysym
        if key == self.key_mapping.get('hold'):
            self.hold_tetrimino()
        if self.lock_movement:
            return
        if key == self.key_mapping.get('soft drop'):
            if self.lock_id is None:
                if self.play_id is not None:
                    self.parent.after_cancel(self.play_id)
                    self.speed_factor = 1/20
                    self.play_game()
                else:
                    self.tetrimino_fall()
        elif self.auto_repeat != key and key == self.key_mapping.get('hard drop'):
            self.tetrimino_drop()
        elif key == self.key_mapping.get('left'):
            self.tetrimino_left()
        elif key == self.key_mapping.get('right'):
            self.tetrimino_right()
        elif self.auto_repeat != key and key == self.key_mapping.get('rotate clockwise'):
            self.tetrimino_rotate(True)
        elif self.auto_repeat != key and key == self.key_mapping.get('rotate counterclockwise'):
            self.tetrimino_rotate(False)
        elif key == 'Return':
            self.game_over.set(True)
        self.auto_repeat = key

    def _keyrelease_dispatch(self, event):
        self.key_time = time.time()
        if event.keysym == self.key_mapping.get('soft drop'):
            self.speed_factor = 1

    def _make_text_label(self, parent, text, font_size, symbol=False):
        if text not in self.texts:
            if not symbol:
                fnt = ImageFont.truetype('assets/Rubik-Medium.ttf', font_size)
            else:
                fnt = ImageFont.truetype('assets/Symbola.ttf', font_size)
            size = fnt.getbbox(text)
            text_img = Image.new('RGBA', (size[2], size[3]), (0, 0, 0, 0))
            d = ImageDraw.Draw(text_img, 'RGBA')
            d.text((0, 0), text, font=fnt)
            text_img = text_img.crop(text_img.getbbox())
            text_tk = ImageTk.PhotoImage(text_img)
            self.texts[text] = text_tk
        else:
            text_tk = self.texts[text]
        text_label = tk.Label(parent, bg='black', bd=0, image=text_tk)
        return text_label

    def show_next_tetriminos(self):
        for row in self.next_area:
            for square in row:
                square.remove_mino()
        start_row = 1
        for tetrimino_type in self.next_tetriminos:
            if tetrimino_type is TetriminoType.I:
                start_row -= 1
            start_col = 1 if tetrimino_type is TetriminoType.O else 0
            tetrimino = Tetrimino(tetrimino_type, (start_col, start_row))
            self.place_tetrimino(tetrimino, self.next_area)
            start_row += 3

    def show_held_tetrimino(self):
        for row in self.hold_area:
            for square in row:
                square.remove_mino()
        if self.held_tetrimino is None:
            return
        row = 0 if self.held_tetrimino.piece_type is TetriminoType.I else 1
        col = 1 if self.held_tetrimino.piece_type is TetriminoType.O else 0
        tetrimino = Tetrimino(self.held_tetrimino.piece_type, (col, row))
        self.place_tetrimino(tetrimino, self.hold_area)

    def show_score(self):
        score_text = self._make_text_label(
            self.score_frame,
            str(self.score),
            Tetris.UI_FONT_SIZE
        )['image']
        self.score_label.config(image=score_text)

    def show_lines(self):
        lines_text = self._make_text_label(
            self.score_frame,
            str(self.lines_cleared),
            Tetris.UI_FONT_SIZE
        )['image']
        self.lines_label.config(image=lines_text)

    def show_level(self):
        level_text = self._make_text_label(
            self.score_frame,
            str(self.level),
            Tetris.UI_FONT_SIZE
        )['image']
        self.level_label.config(image=level_text)

    def show_goal(self):
        goal_text = self._make_text_label(
            self.score_frame,
            str(self.goal),
            Tetris.UI_FONT_SIZE
        )['image']
        self.goal_label.config(image=goal_text)

    def show_ghost_tetrimino(self):
        if not self.ghost_piece:
            return
        while (
            self.check_edge_collision(self.ghost_tetrimino, dr=1) and
            self.check_mino_collision(self.ghost_tetrimino, dr=1)
        ):
            self.ghost_tetrimino.move_vertically(1, 1)
        self.place_tetrimino(self.ghost_tetrimino, self.playfield)

    def generate_seven_bag(self):
        if not self.seven_bag:
            self.seven_bag = [t_type for t_type in TetriminoType]
            shuffle(self.seven_bag)
        for _ in range(Tetris.NEXT_PIECES+1-len(self.next_tetriminos)):
            self.next_tetriminos.append(self.seven_bag.pop(0))

    def random_tetrimino(self):
        self.generate_seven_bag()
        return self.next_tetriminos.pop(0)

    def get_tetrimino_spawn_pos(self, tetrimino_type):
        tetrimino_width = len(tetrimino_type.value[0])
        start_col = (Tetris.COLUMNS - tetrimino_width) // 2
        spawn_pos = (start_col, Tetris.ROWS-3)
        return spawn_pos

    def spawn_tetrimino(self, tetrimino_type):
        if self.game_over.get():
            return
        if self.queued_garbage:
            self.add_garbage()
        self.lock_engaged = False
        spawn_pos = self.get_tetrimino_spawn_pos(tetrimino_type)
        self.falling_lowest = spawn_pos[1]
        self.lock_movement = False
        self.falling_tetrimino = Tetrimino(tetrimino_type, spawn_pos)
        overlap = self.place_tetrimino(self.falling_tetrimino, self.playfield)
        if overlap:
            self.game_over.set(True)
            self.place_tetrimino(self.falling_tetrimino, self.playfield, override=True)
        self.ghost_tetrimino = Tetrimino(tetrimino_type, spawn_pos, True)
        self.show_ghost_tetrimino()
        self.show_next_tetriminos()
        if self.check_mino_collision(self.falling_tetrimino, dr=1):
            self.tetrimino_fall()

    def hold_tetrimino(self):
        if self.has_held or self.falling_tetrimino is None:
            return
        self.remove_tetrimino(self.ghost_tetrimino, self.playfield)
        self.remove_tetrimino(self.falling_tetrimino, self.playfield)
        falling_type = self.held_tetrimino.piece_type if self.held_tetrimino is not None else self.random_tetrimino()
        held_type = self.falling_tetrimino.piece_type
        self.held_tetrimino = Tetrimino(held_type, (0, 0))
        self.spawn_tetrimino(falling_type)
        self.has_held = True
        self.ghost_tetrimino = Tetrimino(self.falling_tetrimino.piece_type, self.falling_tetrimino.upper_left_coords, True)
        self.show_ghost_tetrimino()
        self.show_held_tetrimino()
        self.move_channel.play(Sounds.HOLD)

    def _lock_trace(self, *args):
        lock_moves = self.lock_moves.get()
        if lock_moves == 0:
            self.lock_movement = True
            if self.lock_id is not None:
                self.parent.after_cancel(self.lock_id)
            self.lock_tetrimino()

    def _game_over_trace(self, *args):
        lost = self.game_over.get()
        if lost:
            self.game_lost()

    def lock_tetrimino(self):
        if self.lock_id is not None:
            self.parent.after_cancel(self.lock_id)
            self.lock_id = None
        edges_success = self.check_edge_collision(self.falling_tetrimino, dr=1)
        minos_success = self.check_mino_collision(self.falling_tetrimino, dr=1)
        if edges_success and minos_success:
            return
        t_spin, mini_t_spin = self.detect_t_spin()
        self.lock_moves.set(15)
        self.falling_tetrimino.place()
        visible = False
        for row, *_ in self.falling_tetrimino.get_mino_coords():
            if row >= Tetris.BUFFER_ROWS:
                visible = True
        if not visible:
            self.game_over.set(True)
        lines_cleared = self.clear_lines(t_spin)
        self.has_held = False
        self.update_score(lines_cleared, t_spin, mini_t_spin)
        self.update_lines_cleared(lines_cleared, t_spin, mini_t_spin)
        if lines_cleared == 4:
            self.back_to_back = True
        elif lines_cleared > 0:
            if t_spin or mini_t_spin:
                self.back_to_back = True
        self.spawn_tetrimino(self.random_tetrimino())

    def place_tetrimino(self, tetrimino, area, override=False):
        overlapped = False
        mino_coords = tetrimino.get_mino_coords()
        for row, col, mino in mino_coords:
            if row < 0 or col < 0:
                continue
            square = area[row][col]
            if square.mino is None or override:
                square.place_mino(mino)
            elif square.mino.image is not TetriminoImage.GHOST:
                overlapped = True
        return overlapped

    def remove_tetrimino(self, tetrimino, area):
        mino_coords = tetrimino.get_mino_coords()
        for row, col, _ in mino_coords:
            if row < 0 or col < 0:
                continue
            square = area[row][col]
            square.remove_mino()

    def check_mino_collision(self, tetrimino, dr=0, dc=0):
        mino_coords = tetrimino.get_mino_coords(row_offset=dr, col_offset=dc)
        for row, col, _ in mino_coords:
            if row not in range(Tetris.ROWS+Tetris.BUFFER_ROWS) or col not in range(Tetris.COLUMNS):
                continue
            square = self.playfield[row][col]
            if square.mino is not None:
                if square.mino.placed:
                    return False
        return True

    def check_edge_collision(self, tetrimino, dr=0, dc=0):
        mino_coords = tetrimino.get_mino_coords(row_offset=dr, col_offset=dc)
        bottommost_coord = max(mino_coords, key=lambda c: c[0])[0]
        leftmost_coord = min(mino_coords, key=lambda c: c[1])[1]
        rightmost_coord = max(mino_coords, key=lambda c: c[1])[1]
        return (bottommost_coord <= Tetris.ROWS+Tetris.BUFFER_ROWS - 1 and
            leftmost_coord >= 0 and
            rightmost_coord <= Tetris.COLUMNS - 1)

    def tetrimino_fall(self):
        if self.falling_tetrimino is None:
            return False
        edges_success = self.check_edge_collision(self.falling_tetrimino, dr=1)
        minos_success = self.check_mino_collision(self.falling_tetrimino, dr=1)
        if edges_success and minos_success:
            self.remove_tetrimino(self.ghost_tetrimino, self.playfield)
            self.remove_tetrimino(self.falling_tetrimino, self.playfield)
            self.falling_tetrimino.move_vertically(1, 1)
            self.ghost_tetrimino.upper_left_coords = self.falling_tetrimino.upper_left_coords
            self.place_tetrimino(self.falling_tetrimino, self.playfield)
            self.show_ghost_tetrimino()
            falling_y = self.falling_tetrimino.upper_left_coords[1]
            if falling_y > self.falling_lowest:
                self.lock_moves.set(15)
            self.falling_lowest = max(self.falling_lowest, falling_y)
            if self.placement_mode is PlacementType.CLASSIC and self.lock_id is not None:
                self.parent.after_cancel(self.lock_id)
                self.lock_id = None
            self.rotation_point = None
            if self.speed_factor != 1:
                self.move_channel.play(Sounds.MOVE)
            return True
        else:
            if not self.lock_engaged:
                self.lock_id = self.parent.after(self.lock_time, self.lock_tetrimino)
                self.lock_engaged = True
            return False

    def tetrimino_drop(self):
        if self.falling_tetrimino is None:
            return
        lines_moved = 0
        while (
                self.check_edge_collision(self.falling_tetrimino, dr=1) and
                self.check_mino_collision(self.falling_tetrimino, dr=1)
        ):
            self.tetrimino_fall()
            lines_moved += 1
        self.rotation_point = None
        self.score += 2 * lines_moved
        self.show_score()
        self.lock_tetrimino()

    def tetrimino_left(self):
        if self.falling_tetrimino is None:
            return
        edges_success = self.check_edge_collision(self.falling_tetrimino, dc=-1)
        minos_success = self.check_mino_collision(self.falling_tetrimino, dc=-1)
        if edges_success and minos_success:
            self.remove_tetrimino(self.ghost_tetrimino, self.playfield)
            self.remove_tetrimino(self.falling_tetrimino, self.playfield)
            self.falling_tetrimino.move_horizontally(-1, 1)
            self.ghost_tetrimino.upper_left_coords = self.falling_tetrimino.upper_left_coords
            self.place_tetrimino(self.falling_tetrimino, self.playfield)
            self.show_ghost_tetrimino()
            if self.placement_mode is not PlacementType.CLASSIC and self.lock_id is not None:
                self.parent.after_cancel(self.lock_id)
                self.lock_id = self.parent.after(self.lock_time, self.lock_tetrimino)
                if self.placement_mode is PlacementType.EXTENDED:
                    self.lock_moves.set(self.lock_moves.get() - 1)
            self.rotation_point = None
            self.move_channel.play(Sounds.MOVE)

    def tetrimino_right(self):
        if self.falling_tetrimino is None:
            return
        edges_success = self.check_edge_collision(self.falling_tetrimino, dc=1)
        minos_success = self.check_mino_collision(self.falling_tetrimino, dc=1)
        if edges_success and minos_success:
            self.remove_tetrimino(self.ghost_tetrimino, self.playfield)
            self.remove_tetrimino(self.falling_tetrimino, self.playfield)
            self.falling_tetrimino.move_horizontally(1, 1)
            self.ghost_tetrimino.upper_left_coords = self.falling_tetrimino.upper_left_coords
            self.place_tetrimino(self.falling_tetrimino, self.playfield)
            self.show_ghost_tetrimino()
            if self.placement_mode is not PlacementType.CLASSIC and self.lock_id is not None:
                self.parent.after_cancel(self.lock_id)
                self.lock_id = self.parent.after(self.lock_time, self.lock_tetrimino)
                if self.placement_mode is PlacementType.EXTENDED:
                    self.lock_moves.set(self.lock_moves.get() - 1)
            self.rotation_point = None
            self.move_channel.play(Sounds.MOVE)

    def tetrimino_rotate(self, clockwise):
        if self.falling_tetrimino is None:
            return
        next_rotation = RotationState.get_next_rotation_state(self.falling_tetrimino.rotation_state, clockwise)
        kicks = self.falling_tetrimino.get_wall_kick_tests(next_rotation)
        rotation_successful = False
        kick_used = None
        self.falling_tetrimino.rotate(clockwise)
        for kick_num, kick in enumerate(kicks):
            kick_x, kick_y = kick
            if (self.check_mino_collision(self.falling_tetrimino, dr=kick_y, dc=kick_x) and
                    self.check_edge_collision(self.falling_tetrimino, dr=kick_y, dc=kick_x)):
                rotation_successful = True
                kick_used = kick_x, kick_y
                self.rotation_point = kick_num
                break
        self.falling_tetrimino.rotate(not clockwise)
        if rotation_successful:
            self.rotation_point += 1
            self.remove_tetrimino(self.ghost_tetrimino, self.playfield)
            self.remove_tetrimino(self.falling_tetrimino, self.playfield)
            self.falling_tetrimino.rotate(clockwise)
            self.ghost_tetrimino.rotate(clockwise)
            if x := kick_used[0]:
                self.falling_tetrimino.move_horizontally(int(x/abs(x)), abs(x))
            if y := kick_used[1]:
                self.falling_tetrimino.move_vertically(int(y/abs(y)), abs(y))
            self.ghost_tetrimino.upper_left_coords = self.falling_tetrimino.upper_left_coords
            self.place_tetrimino(self.falling_tetrimino, self.playfield)
            self.show_ghost_tetrimino()
            if self.placement_mode is not PlacementType.CLASSIC and self.lock_id is not None:
                self.parent.after_cancel(self.lock_id)
                self.lock_id = self.parent.after(self.lock_time, self.lock_tetrimino)
                if self.placement_mode is PlacementType.EXTENDED:
                    self.lock_moves.set(self.lock_moves.get() - 1)
            self.move_channel.play(Sounds.MOVE)
        else:
            self.rotation_point = None

    def queue_garbage(self, lines):
        self.queued_garbage += lines
        self.queued_garbage = min(self.queued_garbage, Tetris.TOTAL_HEIGHT)
        if self.queued_garbage > Tetris.ROWS // 2:
            self.line_channel.play(Sounds.HIGH_ALERT)
        elif self.queued_garbage != 0:
            self.line_channel.play(Sounds.LOW_ALERT)
        curr_row = Tetris.TOTAL_HEIGHT - 1
        for _ in range(self.queued_garbage):
            mino = Mino(TetriminoImage.GARBAGE.value, True)
            self.garbage_area[curr_row][0].place_mino(mino)
            curr_row -= 1

    def add_garbage(self):
        for row in range(Tetris.ROWS+Tetris.BUFFER_ROWS):
            for col in range(Tetris.COLUMNS):
                square = self.playfield[row][col]
                if (mino := square.mino) is not None:
                    if row-self.queued_garbage < 0:
                        self.game_over.set(True)
                        break
                    square_above = self.playfield[row-self.queued_garbage][col]
                    square.remove_mino()
                    square_above.place_mino(mino)
        for line in range(self.queued_garbage):
            squares = self.playfield[Tetris.ROWS + Tetris.BUFFER_ROWS - 1 - line]
            empty = randint(0, Tetris.COLUMNS-1)
            for i, square in enumerate(squares):
                if i != empty:
                    mino = Mino(TetriminoImage.GARBAGE.value, True)
                    square.place_mino(mino)
        for row in self.garbage_area:
            row[0].remove_mino()
        self.queued_garbage = 0

    def clear_lines(self, t_spin):
        if self.game_over.get():
            return 0
        runs = []
        run = 0
        bottommost_cleared = 0
        for row, line in enumerate(self.playfield):
            if not any(s.mino for s in line):
                continue
            for square in line:
                if square.mino is None:
                    runs.append(run)
                    run = 0
                    break
            else:
                for square in line:
                    square.remove_mino()
                bottommost_cleared = row
                run += 1
        runs.append(run)

        for run in runs:
            for row in range(bottommost_cleared-run, -1, -1):
                for col in range(Tetris.COLUMNS):
                    square = self.playfield[row][col]
                    if (mino := square.mino) is not None:
                        square_below = self.playfield[row+run][col]
                        if square_below.mino is None:
                            square.remove_mino()
                            square_below.place_mino(mino)

        lines_cleared = sum(runs)
        if lines_cleared == 4 or (lines_cleared == 3 and t_spin):
            self.line_channel.play(Sounds.TETRIS)
        elif lines_cleared > 0:
            self.line_channel.play(Sounds.CLEAR)
        else:
            self.line_channel.play(Sounds.LOCK)
        return lines_cleared

    def detect_t_spin(self):
        if self.falling_tetrimino.piece_type is not TetriminoType.T:
            return False, False
        if self.rotation_point is None:
            return False, False
        corners = self.falling_tetrimino.get_corner_coords()
        if self.falling_tetrimino.rotation_state is RotationState.EAST:
            corners = rotate_matrix(corners, False)
        if self.falling_tetrimino.rotation_state is RotationState.SOUTH:
            corners = rotate_matrix(corners, True)
            corners = rotate_matrix(corners, True)
        if self.falling_tetrimino.rotation_state is RotationState.WEST:
            corners = rotate_matrix(corners, True)
        corners = [coord for row in corners for coord in row]
        minos = []
        for row, col in corners:
            mino = Mino(TetriminoImage.GARBAGE.value, True)
            if row in range(Tetris.ROWS+Tetris.BUFFER_ROWS) and col in range(Tetris.COLUMNS):
                mino = self.playfield[row][col].mino
            minos.append(mino)
        minos = dict(zip('abcd', minos))
        t_spin_found = False
        mini_t_spin_found = False
        if minos['a'] is not None and minos['b'] is not None:
            if minos['c'] is not None or minos['d'] is not None:
                t_spin_found = True
        if minos['c'] is not None and minos['d'] is not None:
            if minos['a'] is not None or minos['b'] is not None:
                mini_t_spin_found = True
        if self.rotation_point == 5:
            t_spin_found = True
            mini_t_spin_found = False
        return t_spin_found, mini_t_spin_found

    def update_score(self, lines, t_spin, mini_t_spin):
        action_total = 0
        if mini_t_spin:
            if lines == 0:
                action_total = 100 * self.level
            elif lines == 1:
                action_total = 200 * self.level
        elif t_spin:
            if lines == 0:
                action_total = 400 * self.level
            elif lines == 1:
                action_total = 800 * self.level
            elif lines == 2:
                action_total = 1200 * self.level
            elif lines == 3:
                action_total = 1600 * self.level
        else:
            if lines in range(1, 4):
                self.back_to_back = False
            if lines == 1:
                action_total = 100 * self.level
            elif lines == 2:
                action_total = 300 * self.level
            elif lines == 3:
                action_total = 500 * self.level
            elif lines == 4:
                action_total = 800 * self.level
        action_total += .5 * action_total * self.back_to_back
        self.score += int(action_total)
        self.show_score()

    def update_lines_cleared(self, lines, t_spin, mini_t_spin):
        cleared_lines = 0
        if self.goal_type is GoalType.FIXED:
            cleared_lines = lines
        elif self.goal_type is GoalType.VARIABLE:
            if mini_t_spin:
                if lines == 0:
                    cleared_lines = 1
                elif lines == 1:
                    cleared_lines = 2
            elif t_spin:
                if lines == 0:
                    cleared_lines = 4
                elif lines == 1:
                    cleared_lines = 8
                elif lines == 2:
                    cleared_lines = 12
                elif lines == 3:
                    cleared_lines = 16
            else:
                if lines == 1:
                    cleared_lines = 1
                elif lines == 2:
                    cleared_lines = 3
                elif lines == 3:
                    cleared_lines = 5
                elif lines == 4:
                    cleared_lines = 8
        self.lines_cleared += cleared_lines
        if self.back_to_back and lines != 0:
            self.lines_cleared *= 1.5
            self.lines_cleared = int(self.lines_cleared)
        self.show_lines()
        if self.lines_cleared >= self.goal:
            self.level = min(Tetris.MAX_LEVEL, self.level+1)
            self.goal = self.get_next_goal()
            self.show_level()
            self.show_goal()

    def get_next_goal(self):
        if self.goal_type is GoalType.VARIABLE:
            return 5 * self.level
        elif self.goal_type is GoalType.FIXED:
            if self.game_started:
                return 10
            else:
                return 10 * self.level

    def sound_toggle(self):
        if self.move_channel.get_volume() == 0:
            self.sound_button.config(image=self.texts['\U0001F50A'])
            self.move_channel.set_volume(0.4)
            self.line_channel.set_volume(0.3)
        else:
            self.move_channel.set_volume(0)
            self.line_channel.set_volume(0)
            self.sound_button.config(image=self.texts['\U0001F507'])

    def music_toggle(self):
        if self.music_channel.get_volume() == 0:
            self.music_button.config(image=self.texts['\U0001D195'])
            self.music_channel.set_volume(0.1)
        else:
            self.music_channel.set_volume(0)
            self.music_button.config(image=self.texts['\U0001D194'])

    def start_up(self):
        start_up_root = tk.Toplevel()
        start_up_root.resizable(0, 0)
        start_up_root.wm_attributes('-type', 'splash')
        start_up_frame = tk.Frame(
            start_up_root,
            bg='black',
            highlightthickness=Tetris.BORDER_WIDTH,
            highlightbackground='white'
        )
        ready_text = self._make_text_label(None, 'Ready?', 22)
        ready_text_height = int(self.parent_root.call(ready_text.cget('image'), 'cget', '-height'))
        ready_text_width = int(self.parent_root.call(ready_text.cget('image'), 'cget', '-width'))
        ready_button = tk.Button(
            start_up_frame,
            bg='black',
            height=ready_text_height+8,
            width=ready_text_width+8,
            image=ready_text.cget('image'),
            bd=0,
            highlightthickness=Tetris.BORDER_WIDTH,
            highlightbackground='white'
        )
        countdown = self._make_text_label(start_up_frame, '', 22)
        countdown.config(height=ready_button.winfo_reqheight(), width=ready_button.winfo_reqwidth())
        countdowns = ['3', '2', '1', 'GO!']

        def sync_windows(event=None):
            if self.game_frame.winfo_rootx() != 0:
                start_up_root.update_idletasks()
            start_up_root_x = self.game_frame.winfo_rootx() + (self.game_frame.winfo_width() - start_up_root.winfo_width())//2
            start_up_root_y = self.game_frame.winfo_rooty() + (self.game_frame.winfo_height() - start_up_root.winfo_height())//2
            start_up_root.geometry(f'+{start_up_root_x}+{start_up_root_y}')

        def display_countdown():
            text = countdowns.pop(0)
            countdown.config(image=self._make_text_label(None, text, 22).cget('image'))
            if text == 'GO!':
                self.move_channel.play(Sounds.GO)
            else:
                self.move_channel.play(Sounds.COUNTDOWN)
            if countdowns:
                start_up_root.after(1000, ready_callback)

        def ready_callback():
            if not countdown.winfo_viewable():
                ready_button.grid_forget()
                countdown.grid(row=0, column=0, pady=10, padx=10)
            display_countdown()
            if not countdowns:
                start_up_root.after(1000, close_and_start)

        def close_and_start():
            self.parent_root.unbind('<Configure>')
            start_up_root.destroy()
            self.play_game()

        ready_button.config(command=ready_callback)
        ready_button.grid(row=0, column=0, pady=10, padx=10)
        start_up_frame.grid(row=0, column=0)
        start_up_root.transient(self.parent_root)
        sync_windows()
        self.parent_root.bind('<Configure>', sync_windows)

    def play_game(self):
        if not self.game_started:
            self.generate_seven_bag()
            self.spawn_tetrimino(self.random_tetrimino())
            self.game_started = True
            self.music_channel.play(Sounds.KOROBEINIKI, loops=-1)

        if self.game_over.get():
            return

        fell = self.tetrimino_fall()
        if self.speed_factor != 1 and fell:
            self.score += 1
            self.show_score()
        game_speed = int(pow((0.8 - ((self.level - 1) * 0.007)), self.level-1) * 1000) * self.speed_factor
        self.play_id = self.parent.after(int(game_speed), self.play_game)

    def pause_game(self):
        if not self.game_started:
            return
        if not self.game_paused:
            self.pause_button.config(image=self.texts['\u23f5'])
            self.music_channel.pause()
            self.move_channel.stop()
            self.move_channel.play(Sounds.COUNTDOWN)
            if self.play_id is not None:
                self.parent.after_cancel(self.play_id)
                self.play_id = None

            for child in self.game_frame.grid_slaves():
                child.grid_forget()
            for child in self.next_frame.grid_slaves():
                child.grid_forget()
            for child in self.hold_frame.grid_slaves():
                child.grid_forget()

            paused_text = self._make_text_label(self.parent, 'PAUSED', Tetris.UI_FONT_SIZE)
            paused_text_height = int(self.parent_root.call(paused_text.cget('image'), 'cget', '-height'))
            paused_text_width = int(self.parent_root.call(paused_text.cget('image'), 'cget', '-width'))
            paused_text_x = self.game_frame.winfo_x() + (self.game_frame.winfo_width() - paused_text_width)//2
            paused_text_y = self.game_frame.winfo_y() + (self.game_frame.winfo_height() - paused_text_height)//2
            paused_text.place(x=paused_text_x, y=paused_text_y)
        else:
            self.pause_button.config(image=self.texts['\u23f8'])
            self._uncover_playfield()
            self._uncover_next_area()
            self._uncover_hold_area()
            for child in self.parent.place_slaves():
                child.place_forget()
            self.move_channel.play(Sounds.GO)
            self.play_game()
            self.music_channel.unpause()
        self.game_paused = not self.game_paused

    def game_lost(self):
        if self.lock_id is not None:
            self.parent.after_cancel(self.lock_id)
        if self.play_id is not None:
            self.parent.after_cancel(self.play_id)
        self.music_channel.stop()
        self.move_channel.stop()
        self.line_channel.stop()
        self.line_channel.play(Sounds.GAME_OVER)

        game_over_root = tk.Toplevel()
        game_over_root.resizable(0, 0)
        game_over_root.wm_attributes('-type', 'splash')
        game_over_frame = tk.Frame(
            game_over_root, bg='black',
            highlightthickness=Tetris.BORDER_WIDTH,
            highlightbackground='white'
        )
        game_over_text = self._make_text_label(game_over_frame, 'Game Over', 30)
        play_again_text = self._make_text_label(game_over_frame, 'Play Again?', 22)
        play_again_text_height = int(self.parent_root.call(play_again_text.cget('image'), 'cget', '-height'))
        play_again_text_width = int(self.parent_root.call(play_again_text.cget('image'), 'cget', '-width'))
        play_again_button = tk.Button(
            game_over_frame,
            bg='black',
            height=play_again_text_height+8,
            width=play_again_text_width+8,
            image=play_again_text.cget('image'),
            bd=0,
            highlightthickness=Tetris.BORDER_WIDTH,
            highlightbackground='white'
        )

        def sync_windows(event=None):
            if self.game_frame.winfo_rootx() != 0:
                game_over_root.update_idletasks()
            game_over_root_x = self.game_frame.winfo_rootx() + (self.game_frame.winfo_width() - game_over_root.winfo_width())//2
            game_over_root_y = self.game_frame.winfo_rooty() + (self.game_frame.winfo_height() - game_over_root.winfo_height())//2
            game_over_root.geometry(f'+{game_over_root_x}+{game_over_root_y}')

        def play_again_callback():
            self.parent_root.unbind('<Configure>')
            game_over_root.destroy()
            self.reset_game()

        play_again_button.config(command=play_again_callback)
        game_over_text.grid(row=0, column=0, pady=10, padx=10)
        if self.allow_play_again:
            play_again_button.grid(row=1, column=0, pady=10, padx=10)
        game_over_frame.grid(row=0, column=0)
        game_over_root.transient(self.parent_root)
        sync_windows()
        self.parent_root.bind('<Configure>', sync_windows)

    def reset_game(self):
        for row in self.playfield:
            for square in row:
                square.remove_mino()
        self.game_started = False
        self.falling_lowest = 0
        self.level = self.starting_level
        self.score = 0
        self.back_to_back = False
        self.lines_cleared = 0
        self.goal = self.get_next_goal()
        self.play_id = None
        self.lock_moves.set(15)
        self.lock_movement = False
        self.lock_id = None
        self.auto_repeat = ''
        self.key_time = 0
        self.speed_factor = 1
        self.rotation_point = None
        self.falling_tetrimino = None
        self.held_tetrimino = None
        self.ghost_tetrimino = None
        self.game_paused = False
        self.game_over.set(False)
        self.has_held = False
        self.queued_garbage = 0
        self.next_tetriminos = []
        self.seven_bag = []
        self.show_next_tetriminos()
        self.show_held_tetrimino()
        self.show_score()
        self.show_lines()
        self.show_level()
        self.show_goal()
        self.queue_garbage(0)
        if self.start_menu:
            self.start_up()


if __name__ == '__main__':
    mixer.pre_init(buffer=4096)
    mixer.init()
    tetris_music = mixer.Channel(0)
    tetris_move = mixer.Channel(1)
    tetris_line = mixer.Channel(2)
    root = tk.Tk()
    root.resizable(0, 0)
    root.title('Tetris')
    tetris_frame = tk.Frame(root)
    keys = {
        'soft drop': 's',
        'hard drop': 'w',
        'left': 'a',
        'right': 'd',
        'rotate clockwise': 'x',
        'rotate counterclockwise': 'z',
        'hold': 'c'
    }
    tetris = Tetris(
        parent=tetris_frame,
        mirror_ui=False,
        ghost_piece = True,
        placement_mode=PlacementType.EXTENDED,
        starting_level=1,
        goal_type=GoalType.VARIABLE,
        key_mapping=keys,
        allow_pausing=True,
        music_channel=tetris_music,
        move_channel=tetris_move,
        line_channel=tetris_line,
        start_menu=True,
        allow_play_again=True
    )
    tetris_frame.grid(row=0, column=0)
    root.mainloop()
