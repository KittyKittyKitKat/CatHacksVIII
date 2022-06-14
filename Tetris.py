import tkinter as tk
import time
from enum import Enum, auto
from random import shuffle, randint
from PIL import Image, ImageDraw, ImageFont, ImageTk

def transpose(matrix):
    return [[matrix[j][i] for j in range(len(matrix))] for i in range(len(matrix[0]))]

def reverse_rows(matrix):
    return matrix[::-1]

def reverse_columns(matrix):
    return [row[::-1] for row in matrix]

class PlacementType(Enum):
    EXTENDED = auto()
    INFINITE = auto()
    CLASSIC = auto()


class TetriminoImage(Enum):
    I = Image.open('assets/tetris/cyan.png')
    J = Image.open('assets/tetris/blue.png')
    L = Image.open('assets/tetris/orange.png')
    O = Image.open('assets/tetris/yellow.png')
    T = Image.open('assets/tetris/purple.png')
    S = Image.open('assets/tetris/green.png')
    Z = Image.open('assets/tetris/red.png')
    GHOST = Image.open('assets/tetris/ghost.png')
    GARBAGE = Image.open('assets/tetris/garbage.png')


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
    SPAWN = auto()
    CLOCKWISE = auto()
    FLIPPED = auto()
    COUNTERCLOCKWISE = auto()

    @classmethod
    def get_next_rotation_state(cls, starting_rotation, clockwise):
        new_rotation_state = None
        if clockwise:
            match starting_rotation:
                case RotationState.SPAWN:
                    new_rotation_state = RotationState.CLOCKWISE
                case RotationState.CLOCKWISE:
                    new_rotation_state = RotationState.FLIPPED
                case RotationState.FLIPPED:
                    new_rotation_state = RotationState.COUNTERCLOCKWISE
                case RotationState.COUNTERCLOCKWISE:
                    new_rotation_state = RotationState.SPAWN
        else:
            match starting_rotation:
                case RotationState.SPAWN:
                    new_rotation_state = RotationState.COUNTERCLOCKWISE
                case RotationState.CLOCKWISE:
                    new_rotation_state = RotationState.SPAWN
                case RotationState.FLIPPED:
                    new_rotation_state = RotationState.CLOCKWISE
                case RotationState.COUNTERCLOCKWISE:
                    new_rotation_state = RotationState.FLIPPED
        return new_rotation_state


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
        self.rotation_state = RotationState.SPAWN
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
            case RotationState.SPAWN, RotationState.CLOCKWISE:
                if self.piece_type is TetriminoType.I:
                    kicks =  [(-2, 0), (1, 0), (-2, 1), (1, -2)]
                else:
                    kicks =  [(-1, 0), (-1, -1), (0, 2), (-1, 2)]
            case RotationState.CLOCKWISE, RotationState.SPAWN:
                if self.piece_type is TetriminoType.I:
                    kicks =  [(2, 0), (-1, 0), (2, -1), (-1, 2)]
                else:
                    kicks =  [(1, 0), (1, 1), (0, -2), (1, -2)]
            case RotationState.CLOCKWISE, RotationState.FLIPPED:
                if self.piece_type is TetriminoType.I:
                    kicks =  [(-1, 0), (2, 0), (-1, -2), (2, 1)]
                else:
                    kicks =  [(1, 0), (1, 1), (0, -2), (1, -2)]
            case RotationState.FLIPPED, RotationState.CLOCKWISE:
                if self.piece_type is TetriminoType.I:
                    kicks =  [(1, 0), (-2, 0), (1, 2), (-2, -1)]
                else:
                    kicks =  [(-1, 0), (-1, -1), (0, 2), (-1, 2)]
            case RotationState.FLIPPED, RotationState.COUNTERCLOCKWISE:
                if self.piece_type is TetriminoType.I:
                    kicks =  [(2, 0), (-1, 0), (2, -1), (-1, 2)]
                else:
                    kicks =  [(1, 0), (1, -1), (0, 2), (1, 2)]
            case RotationState.COUNTERCLOCKWISE, RotationState.FLIPPED:
                if self.piece_type is TetriminoType.I:
                    kicks =  [(-2, 0), (1, 0), (-2, 1), (1, -2)]
                else:
                    kicks =  [(-1, 0), (-1, 1), (0, -2), (-1, -2)]
            case RotationState.COUNTERCLOCKWISE, RotationState.SPAWN:
                if self.piece_type is TetriminoType.I:
                    kicks =  [(1, 0), (-2, 0), (1, 2), (-2, -1)]
                else:
                    kicks =  [(-1, 0), (-1, 1), (0, -2), (-1, -2)]
            case RotationState.SPAWN, RotationState.COUNTERCLOCKWISE:
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

    def place(self):
        self.placed = True
        for row in self.minos:
            for mino in row:
                if isinstance(mino, Mino):
                    mino.placed = True

    def rotate(self, clockwise):
        if clockwise:
            self.minos = reverse_columns(transpose(self.minos))
        else:
            self.minos = reverse_rows(transpose(self.minos))
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
        super().__init__(parent, width=Square.SQUARE_SIZE, height=Square.SQUARE_SIZE, bd=0, image=self.tk_image)

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
    UI_FONT_SIZE = 20
    BORDER_WIDTH = 2
    UI_INNER_PADDING = 6
    TOTAL_HEIGHT = 24
    SKYLINE_VISIBILITY = 8
    MAX_LEVEL = 15

    def __init__(self, parent, ui_on_right, ghost_piece, placement_mode, key_mapping):
        self.parent = parent
        self.ui_on_right = ui_on_right
        self.ghost_piece = ghost_piece
        self.placement_mode = placement_mode
        self.key_mapping = key_mapping
        self.parent_root = parent.winfo_toplevel()
        self.game_frame = tk.Frame(self.parent)
        self.ui_frame = tk.Frame(self.parent)
        self.next_frame = tk.Frame(self.parent)
        self.hold_frame = tk.Frame(self.parent)
        self.score_frame = tk.Frame(self.parent)
        self.texts = {}
        self.lock_time = 500
        self.falling_lowest = 0
        self.level = 1
        self.play_id = None
        self.lock_moves = tk.IntVar(master=self.parent, value=15)
        self.lock_movement = False
        self.lock_id = None
        self.auto_repeat = ''
        self.key_time = 0
        self.speed_factor = 1
        self.falling_tetrimino = None
        self.held_tetrimino = None
        self.ghost_tetrimino = None
        self.game_started = False
        self.game_over = False
        self.has_held = False
        self.queued_garbage = 0
        self.next_tetriminos = []
        self.seven_bag = []
        self.playfield = []
        self.next_area = []
        self.hold_area = []
        self.empty_image = Image.new('RGBA', (Square.SQUARE_SIZE, Square.SQUARE_SIZE), (0, 0, 0))
        self._config_widgets()
        self._set_up_playfield()
        self._set_up_next_area()
        self._set_up_hold_area()
        self._set_up_score_area()
        self._set_up_keybindings()
        self.lock_trace_id = self.lock_moves.trace_add('write', self._lock_trace)
        self.start_up()

    def _config_widgets(self):
        self.parent.config(
            bg='black',
            height=Square.SQUARE_SIZE*Tetris.TOTAL_HEIGHT+2*Tetris.BORDER_WIDTH+Tetris.SKYLINE_VISIBILITY,
            width=Square.SQUARE_SIZE*(Tetris.COLUMNS+Tetris.UI_COLUMNS)+4*Tetris.BORDER_WIDTH+2*Tetris.UI_INNER_PADDING,
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
            bg='red',
            width=Square.SQUARE_SIZE*Tetris.COLUMNS+2*Tetris.BORDER_WIDTH,
            height=Square.SQUARE_SIZE*(Tetris.TOTAL_HEIGHT-Tetris.ROWS),
            highlightbackground='white',
            highlightthickness=Tetris.BORDER_WIDTH
        )
        self.parent.grid_propagate(False)
        self.game_frame.grid_propagate(False)
        self.next_frame.grid_propagate(False)
        self.hold_frame.grid_propagate(False)
        self.score_frame.grid_propagate(False)
        self.next_frame.columnconfigure(0, weight=1)
        self.next_frame.columnconfigure(4, weight=1)
        self.hold_frame.columnconfigure(0, weight=1)
        self.hold_frame.columnconfigure(4, weight=1)
        self.game_frame.rowconfigure(0, weight=1)
        self.ui_frame.grid(row=0, column=int(self.ui_on_right), rowspan=4)

    def _set_up_playfield(self):
        for row in range(Tetris.ROWS+Tetris.BUFFER_ROWS):
            well_row = []
            for col in range(Tetris.COLUMNS):
                square = Square(self.game_frame, self.empty_image)
                if row >= Tetris.BUFFER_ROWS-1:
                    square.grid(row=row-Tetris.ROWS+1, column=col, sticky=tk.N)
                well_row.append(square)
            self.playfield.append(well_row)
        self.game_frame.grid(row=0, column=int(not self.ui_on_right), rowspan=4)

    def _set_up_next_area(self):
        for row in range(Tetris.NEXT_ROWS):
            well_row = []
            for col in range(Tetris.UI_COLUMNS):
                square = Square(self.next_frame, self.empty_image)
                square.grid(row=row, column=col+1, sticky=tk.W)
                well_row.append(square)
            self.next_area.append(well_row)
        self.next_frame.grid(row=3, column=int(self.ui_on_right), rowspan=2)
        next_label = self._make_text_label(self.parent, 'NEXT', Tetris.UI_FONT_SIZE)
        next_label.grid(row=2, column=int(self.ui_on_right))

    def _set_up_hold_area(self):
        for row in range(Tetris.HOLD_ROWS):
            well_row = []
            for col in range(Tetris.UI_COLUMNS):
                square = Square(self.hold_frame, self.empty_image)
                square.grid(row=row, column=col+1, sticky=tk.W)
                well_row.append(square)
            self.hold_area.append(well_row)
        self.hold_frame.grid(row=1, column=int(self.ui_on_right))
        hold_label = self._make_text_label(self.parent, 'HOLD', Tetris.UI_FONT_SIZE)
        hold_label.grid(row=0, column=int(self.ui_on_right))

    def _set_up_score_area(self):
        score_label = self._make_text_label(self.score_frame, 'SCORE', Tetris.UI_FONT_SIZE)
        score_label.grid(row=0, column=0)
        self.score_frame.grid(row=4, column=int(not self.ui_on_right))

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
        self.parent.bind('<KeyPress>', self._keypress_dispatch)
        self.parent.bind('<KeyRelease>', self._keyrelease_dispatch)
        self.parent.focus_set()

    def _keypress_dispatch(self, event):
        if self.game_over:
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
        self.auto_repeat = key

    def _keyrelease_dispatch(self, event):
        self.key_time = time.time()
        if event.keysym == self.key_mapping.get('soft drop'):
            self.speed_factor = 1

    def _make_text_label(self, parent, text, font_size):
        if text not in self.texts:
            fnt = ImageFont.truetype('assets/Rubik-Medium.ttf', font_size)
            size = fnt.getsize(text)
            text_img = Image.new('RGBA', size, (0, 0, 0))
            d = ImageDraw.Draw(text_img, 'RGBA')
            d.text((0, 0), text, font=fnt)
            text_tk = ImageTk.PhotoImage(text_img)
            self.texts[text] = text_tk
        else:
            text_tk = self.texts[text]
        text_label = tk.Label(parent, bd=0, image=text_tk)
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

    def show_ghost_tetrimino(self):
        if not self.ghost_piece:
            return
        while (
            self.check_edge_collision(self.ghost_tetrimino, dr=1) and
            self.check_mino_collision(self.ghost_tetrimino, dr=1)
        ):
            self.ghost_tetrimino.move_vertically(1, 1)
        self.place_tetrimino(self.ghost_tetrimino, self.playfield)

    def generate_tetriminos(self):
        if not self.seven_bag:
            self.seven_bag = [t_type for t_type in TetriminoType]
            shuffle(self.seven_bag)
        for i in range(Tetris.NEXT_PIECES+1-len(self.next_tetriminos)):
            self.next_tetriminos.append(self.seven_bag.pop(0))

    def random_tetrimino(self):
        self.generate_tetriminos()
        return self.next_tetriminos.pop(0)

    def get_tetrimino_spawn_pos(self, tetrimino_type):
        tetrimino_width = len(tetrimino_type.value[0])
        start_col = (Tetris.COLUMNS - tetrimino_width) // 2
        spawn_pos = (start_col, Tetris.ROWS-2)
        return spawn_pos

    def spawn_tetrimino(self, tetrimino_type):
        spawn_pos = self.get_tetrimino_spawn_pos(tetrimino_type)
        self.falling_lowest = spawn_pos[1]
        self.lock_movement = False
        self.falling_tetrimino = Tetrimino(tetrimino_type, spawn_pos)
        overlap = self.place_tetrimino(self.falling_tetrimino, self.playfield)
        if overlap:
            self.game_over = True
            overlap = self.place_tetrimino(self.falling_tetrimino, self.playfield, override=True)
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

    def _lock_trace(self, *args):
        lock_moves = self.lock_moves.get()
        if lock_moves == 0:
            self.lock_movement = True
            if self.lock_id is not None:
                self.parent.after_cancel(self.lock_id)
            self.lock_tetrimino()

    def lock_tetrimino(self):
        self.lock_id = None
        edges_success = self.check_edge_collision(self.falling_tetrimino, dr=1)
        minos_success = self.check_mino_collision(self.falling_tetrimino, dr=1)
        if edges_success and minos_success:
            return
        self.lock_moves.set(15)
        self.falling_tetrimino.place()
        self.clear_lines()
        self.has_held = False
        if self.queued_garbage:
            self.add_garbage()
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
            return
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
        else:
            if self.lock_id is not None:
                self.parent.after_cancel(self.lock_id)
            self.lock_id = self.parent.after(self.lock_time, self.lock_tetrimino)

    def tetrimino_drop(self):
        if self.falling_tetrimino is None:
            return
        while (
                self.check_edge_collision(self.falling_tetrimino, dr=1) and
                self.check_mino_collision(self.falling_tetrimino, dr=1)
        ):
            self.tetrimino_fall()
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

    def tetrimino_rotate(self, clockwise):
        if self.falling_tetrimino is None:
            return
        next_rotation = RotationState.get_next_rotation_state(self.falling_tetrimino.rotation_state, clockwise)
        kicks = self.falling_tetrimino.get_wall_kick_tests(next_rotation)
        rotation_successful = False
        kick_used = None
        self.falling_tetrimino.rotate(clockwise)
        for kick_x, kick_y in kicks:
            if (self.check_mino_collision(self.falling_tetrimino, dr=kick_y, dc=kick_x) and
                    self.check_edge_collision(self.falling_tetrimino, dr=kick_y, dc=kick_x)):
                rotation_successful = True
                kick_used = kick_x, kick_y
                break
        self.falling_tetrimino.rotate(not clockwise)
        if rotation_successful:
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

    def add_garbage(self):
        for row in range(Tetris.BUFFER_ROWS, Tetris.ROWS+Tetris.BUFFER_ROWS):
            for col in range(Tetris.COLUMNS):
                square = self.playfield[row][col]
                if (mino := square.mino) is not None:
                    if row-self.queued_garbage < 0:
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
        self.queued_garbage = 0

    def clear_lines(self):
        if self.game_over:
            return
        runs = []
        run = 0
        bottommost_cleared = 0
        for row, line in enumerate(self.playfield):
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

    def start_up(self):
        start_up_root = tk.Toplevel()
        start_up_root.resizable(0, 0)
        start_up_root.wm_attributes('-type', 'splash')
        start_up_frame = tk.Frame(
            start_up_root, bg='black',
            highlightthickness=Tetris.BORDER_WIDTH,
            highlightbackground='white'
        )
        ready_text = self._make_text_label(start_up_frame, 'Ready?', 22)
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

        def sync_windows(event=None):
            if self.game_frame.winfo_rootx() != 0:
                start_up_root.update_idletasks()
            start_up_root_x = self.game_frame.winfo_rootx() + (self.game_frame.winfo_width() - start_up_root.winfo_width())//2
            start_up_root_y = self.game_frame.winfo_rooty() + (self.game_frame.winfo_height() - start_up_root.winfo_height())//2
            start_up_root.geometry(f'+{start_up_root_x}+{start_up_root_y}')

        def ready_callback():
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
            self.generate_tetriminos()
            self.spawn_tetrimino(self.random_tetrimino())
            self.game_started = True

        if self.game_over:
            if self.lock_id is not None:
                self.parent.after_cancel(self.lock_id)
            self.parent.after_cancel(self.play_id)
            self.game_lost()
            return

        self.tetrimino_fall()
        game_speed = int(pow((0.8 - ((self.level - 1) * 0.007)), self.level-1) * 1000) * self.speed_factor
        self.play_id = self.parent.after(int(game_speed), self.play_game)

    def game_lost(self):
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
        play_again_button.grid(row=1, column=0, pady=10, padx=10)
        game_over_frame.grid(row=0, column=0)
        game_over_root.transient(self.parent_root)
        sync_windows()
        self.parent_root.bind('<Configure>', sync_windows)

    def reset_game(self):
        for row in self.playfield:
            for square in row:
                square.remove_mino()
        self.falling_lowest = 0
        self.level = 1
        self.play_id = None
        self.lock_moves.set(15)
        self.lock_movement = False
        self.lock_id = None
        self.auto_repeat = ''
        self.key_time = 0
        self.speed_factor = 1
        self.falling_tetrimino = None
        self.held_tetrimino = None
        self.ghost_tetrimino = None
        self.game_started = False
        self.game_over = False
        self.has_held = False
        self.queued_garbage = 0
        self.next_tetriminos = []
        self.seven_bag = []
        self.show_next_tetriminos()
        self.show_held_tetrimino()
        self.start_up()


if __name__ == '__main__':
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
        ui_on_right=False,
        ghost_piece = True,
        placement_mode=PlacementType.CLASSIC,
        key_mapping=keys
    )
    tetris_frame.grid(row=0, column=0)
    root.mainloop()
