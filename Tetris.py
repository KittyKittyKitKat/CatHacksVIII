from enum import Enum, auto
import json
import tkinter as tk
from PIL import Image, ImageTk

def flatten(matrix):
    return [item for row in matrix for item in row]


def transpose(matrix):
    return [[matrix[j][i] for j in range(len(matrix))] for i in range(len(matrix[0]))]


def reverse_rows(matrix):
    return matrix[::-1]


def reverse_columns(matrix):
    return [row[::-1] for row in matrix]

class Constants:
    columns = 10
    row = 20

class SquareState(Enum):
    EMPTY = auto()
    PLACED = auto()
    FALLING = auto()
    ROTATING = auto()


class TetrominoType(Enum):
    L = 'L'
    I = 'I'
    J = 'J'
    O = 'O'
    S = 'S'
    Z = 'Z'
    T = 'T'

    def __new__(cls, dict_key):
        obj = object.__new__(cls)
        with open('tetrominos.json') as fp:
            tetromino_data = json.load(fp)
        obj._value_ = tetromino_data[dict_key]
        return obj


class TetrominoSquare(tk.Label):
    def __init__(self, parent, size, tk_image, state):
        super().__init__(parent, height=size, width=size, im=tk_image, bd=0, bg='black')
        self.state = state

    def regrid(self, new_row, new_col):
        self.grid_forget()
        self.grid(row=new_row, column=new_col)

class Tetromino:
    def __init__(self, parent, piece_type):
        self.parent = parent
        self.piece_type = piece_type
        self.squares = [
            [TetrominoSquare(
                parent,
                16,
                ImageTk.PhotoImage(Image.new('RGBA', (16, 16), '#ff0000')), #TODO: Add colours
                SquareState.FALLING
            ) if col == 1 else [None, None] for col in row]
            for row in self.piece_type.value
        ]
        self.squares_flat = [sq for sq in flatten(self.squares) if isinstance(sq, TetrominoSquare)]

    def set_state(self, state):
        for square in self.squares_flat:
            square.state = state

    def generate_coords_matrix(self, col_offest, row_offset):
        coords = []
        for row in self.squares:
            coords_row = []
            for square in row:
                if isinstance(square, TetrominoSquare):
                    x, y = square.grid_info()['column'], square.grid_info()['row']
                else:
                    x, y = square
                coords_row.append((x + col_offest, y + row_offset))
            coords.append(coords_row)
        return coords

    def find_placed_blocks(self, axis: str, direction: int) -> list[TetrominoSquare]:
        found_squares = []
        for square in self.squares_flat:
            sq_row = square.grid_info()['row']
            sq_col = square.grid_info()['column']
            check_row = sq_row + direction if axis == 'row' else sq_row
            check_col = sq_col + direction if axis == 'col' else sq_col
            sqs_found = [sq for sq in self.master.grid_slaves(row=check_row, column=check_col) if sq.status is SquareState.PLACED]
            if sqs_found:
                found_squares.extend(sqs_found)
        return found_squares

    def rotate(self, cw):
        coords = self.generate_coords_matrix()
        if cw:
            rotated_coords = flatten(reverse_columns(transpose(coords)))
        else:
            rotated_coords = flatten(reverse_rows(transpose(coords)))
        coords = flatten(coords)
        for pair, pair_rot in zip(coords, rotated_coords):
            old_x, old_y = pair
            new_x, new_y = pair_rot
            pair_off_grid = old_x not in range(Constants.cols) or old_y not in range(Constants.rows)
            pair_rot_off_grid = new_x not in range(Constants.cols) or new_y not in range(Constants.rows)
            empty = []
            if not pair_off_grid:
                empty = [sq for sq in self.master.grid_slaves(row=old_y, column=old_x) if sq.status is SquareState.EMPTY]
            falling = []
            if not pair_rot_off_grid:
                falling = [sq for sq in self.master.grid_slaves(row=new_y, column=new_x) if sq.status is SquareState.FALLING]
            if falling and not empty:
                return False
            placed = []
            if not pair_off_grid:
                placed = [sq for sq in self.master.grid_slaves(row=old_y, column=old_x) if sq.status is SquareState.PLACED]
            if falling and not self.are_colours_compatible(placed):
                return False
        for old_coords, new_coords in zip(coords, rotated_coords):
            old_x, old_y = old_coords
            new_x, new_y = new_coords
            try:
                square = [sq for sq in self.master.grid_slaves(row=new_y, column=new_x) if sq.status is SquareState.FALLING]
            except tk.TclError:
                continue
            if square:
                square = square[0]
                square.status = SquareState.ROTATING
                square.regrid(old_y, old_x)
        if cw:
            self.squares = reverse_columns(transpose(self.squares))
        else:
            self.squares = reverse_rows(transpose(self.squares))
        self.squares_flat = [sq for sq in flatten(self.squares) if isinstance(sq, TetrominoSquare)]
        self.grid(min(x for x, _ in rotated_coords), min(y for _, y in rotated_coords))
        self.set_status(SquareState.FALLING)
        return True

    def move_left(self):
        if not min([sq.grid_info()['column'] for sq in self.squares_flat]):
            return False
        if self.find_placed_blocks('col', -1):
            return False
        for row in self.squares:
            for square in row:
                if isinstance(square, TetrominoSquare):
                    gi = square.grid_info()
                    row, new_col = gi['row'], gi['column'] - 1
                    square.regrid(row, new_col)
                else:
                    square[0], square[1] = square[0] - 1, square[1]
        return True

    def move_right(self):
        if max([sq.grid_info()['column'] for sq in self.squares_flat]) == Constants.cols - 1:
            return False
        if self.find_placed_blocks('col', 1):
            return False
        for row in self.squares:
            for square in reversed(row):
                if isinstance(square, TetrominoSquare):
                    gi = square.grid_info()
                    row, new_col = gi['row'], gi['column'] + 1
                    square.regrid(row, new_col)
                else:
                    square[0], square[1] = square[0] + 1, square[1]
        return True

    def move_down(self):
        if max([sq.grid_info()['row'] for sq in self.squares_flat]) == Constants.rows - 1:
            return False
        if self.find_placed_blocks('row', 1):
            return False
        for row in reversed(self.squares):
            for square in row:
                if isinstance(square, TetrominoSquare):
                    gi = square.grid_info()
                    new_row, col = gi['row'] + 1, gi['column']
                    square.regrid(new_row, col)
                else:
                    square[0], square[1] = square[0], square[1] + 1

        return True

    def get_future_coords(self, leftmost_x: int, upmost_y: int) -> list[list[list[int]]]:
        future_grid = [
            [[0, 0] if col == 1 else None for col in row]
            for row in self.piece_type.value[0]
        ]
        future_coords = []

        current_y = upmost_y
        for i, row in enumerate(future_grid):
            if i == 0:
                if not any(row):
                    current_y -= 1

            current_x = leftmost_x
            for square in row:
                if square is not None:
                    future_coords.append([current_x, current_y])
                current_x += 1
            current_y += 1

        return future_coords

    def grid(self, leftmost_x: int, upmost_y: int) -> None:
        current_y = upmost_y
        for i, row in enumerate(self.squares):
            if i == 0:
                for square in row:
                    if square != [None, None]:
                        break
                else:
                    current_y -= 1
            current_x = leftmost_x
            for square in row:
                if isinstance(square, TetrominoSquare):
                    square.grid(row=current_y, column=current_x)
                else:
                    square[0], square[1] = current_x, current_y
                current_x += 1
            current_y += 1

    def change_master(self, new_master: tk.Widget) -> None:
        for square in self.squares_flat:
            square.grid_forget()
        self.__init__(new_master, self.colour, self.piece_type)



class Tetris:
    def __init__(self):
        ...