from random import choice
import tkinter as tk
from enum import Enum, auto
from PIL import Image, ImageTk

def flatten(matrix):
    return [item for row in matrix for item in row]

def transpose(matrix):
    return [[matrix[j][i] for j in range(len(matrix))] for i in range(len(matrix[0]))]

def reverse_rows(matrix):
    return matrix[::-1]

def reverse_columns(matrix):
    return [row[::-1] for row in matrix]

class TetrominoColour(Enum):
    I = Image.open('cyan.png')
    J = Image.open('blue.png')
    L = Image.open('orange.png')
    O = Image.open('yellow.png')
    T = Image.open('purple.png')
    S = Image.open('green.png')
    Z = Image.open('red.png')

class TetrominoType(Enum):
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

class SquareStatus(Enum):
    PLACED = auto()
    FALLING = auto()
    ROTATING = auto()

class TetrominoSquare(tk.Label):
    def __init__(self, parent, size, image, status):
        self.image = image
        self.tk_image = ImageTk.PhotoImage(image)
        self.status = status
        super().__init__(parent, height=size, width=size, im=self.tk_image, bd=0, bg='black')

    def redraw(self, new_row, new_col):
        self.grid_forget()
        self.grid(row=new_row, column=new_col)

class Tetromino:
    def __init__(self, parent, piece_type):
        self.parent = parent
        self.piece_type = piece_type
        self.squares = [
            [TetrominoSquare(
                parent,
                Tetris.SQUARE_SIZE,
                TetrominoColour[piece_type.name].value,
                SquareStatus.FALLING
            ) if col == 1 else [None, None] for col in row]
            for row in self.piece_type.value
        ]
        self.squares_flat = [sq for sq in flatten(self.squares) if isinstance(sq, TetrominoSquare)]

    def set_status(self, status):
        for square in self.squares_flat:
            square.status = status

    def generate_coords_matrix(self, col_offset=0, row_offset=0):
        coords = []
        for row in self.squares:
            coords_row = []
            for square in row:
                if isinstance(square, TetrominoSquare):
                    x, y = square.grid_info()['column'], square.grid_info()['row']
                else:
                    x, y = square
                coords_row.append((x + col_offset, y + row_offset))
            coords.append(coords_row)
        return coords

    def find_placed_blocks(self, axis, direction):
        found_squares = []
        for square in self.squares_flat:
            sq_row = square.grid_info()['row']
            sq_col = square.grid_info()['column']
            check_row = sq_row + direction if axis == 'row' else sq_row
            check_col = sq_col + direction if axis == 'col' else sq_col
            sqs_found = [sq for sq in self.parent.grid_slaves(row=check_row, column=check_col) if isinstance(sq, TetrominoSquare) and sq.status is SquareStatus.PLACED]
            if sqs_found:
                found_squares.extend(sqs_found)
        return found_squares

    def grid(self, leftmost_x, upmost_y):
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
                    square.redraw(row, new_col)
                else:
                    square[0], square[1] = square[0] - 1, square[1]
        return True

    def move_right(self):
        if max([sq.grid_info()['column'] for sq in self.squares_flat]) == Tetris.COLUMNS - 1:
            return False
        if self.find_placed_blocks('col', 1):
            return False
        for row in self.squares:
            for square in reversed(row):
                if isinstance(square, TetrominoSquare):
                    gi = square.grid_info()
                    row, new_col = gi['row'], gi['column'] + 1
                    square.redraw(row, new_col)
                else:
                    square[0], square[1] = square[0] + 1, square[1]
        return True

    def move_down(self):
        if max([sq.grid_info()['row'] for sq in self.squares_flat]) == Tetris.ROWS - 1:
            return False
        if self.find_placed_blocks('row', 1):
            return False
        for row in reversed(self.squares):
            for square in row:
                if isinstance(square, TetrominoSquare):
                    gi = square.grid_info()
                    new_row, col = gi['row'] + 1, gi['column']
                    square.redraw(new_row, col)
                else:
                    square[0], square[1] = square[0], square[1] + 1
        return True

    def rotate(self, cw: bool):
        # Generate a matrix with the coordinates if the bounding box of the piece
        coords = self.generate_coords_matrix()
        # Rotate the matrix clockwise if cw and counterclockwise otherwise, then flatten
        if cw:
            rotated_coords = flatten(reverse_columns(transpose(coords)))
        else:
            rotated_coords = flatten(reverse_rows(transpose(coords)))
        # Flatten the coords. Flattening is done to make iterating in parallel easier
        coords = flatten(coords)

        # First iteration over the coords in parallel. This does all the necessary checks to see if the piece can be rotated
        for pair, pair_rot in zip(coords, rotated_coords):
            # Unpack the pairs into their col, row coordinates
            old_x, old_y = pair
            new_x, new_y = pair_rot

            # Check if the pairs are off the edges of the grid, and store that
            pair_off_grid = old_x not in range(Tetris.COLUMNS) or old_y not in range(Tetris.ROWS)
            pair_rot_off_grid = new_x not in range(Tetris.COLUMNS) or new_y not in range(Tetris.ROWS)

            # Store the potential empty square at the current position
            empty = []
            if not pair_off_grid:
                empty = [sq for sq in self.parent.grid_slaves(row=old_y, column=old_x) if not isinstance(sq, TetrominoSquare)]

            # Store the potential falling square at the rotated position
            falling = []
            if not pair_rot_off_grid:
                falling = [sq for sq in self.parent.grid_slaves(row=new_y, column=new_x) if isinstance(sq, TetrominoSquare) and sq.status is SquareStatus.FALLING]

            # If there is a falling square but no empty square for it go, the rotation failed, so return
            if falling and not empty:
                return False

            # Store the potential placed square at the rotated position
            placed = []
            if not pair_off_grid:
                placed = [sq for sq in self.parent.grid_slaves(row=old_y, column=old_x) if isinstance(sq, TetrominoSquare) and sq.status is SquareStatus.PLACED]

            # If there is a falling square and a placed square with incompatible colours, the rotation failed
            if falling and placed:
                return False

        # Second iteration over the coordinates. This actually rotates the pieces
        for old_coords, new_coords in zip(coords, rotated_coords):
            # Unpack the pairs into their col, row coordinates
            old_x, old_y = old_coords
            new_x, new_y = new_coords

            # Try to get the falling square. Try except guards against new_y, new_x < 0
            try:
                square = [sq for sq in self.parent.grid_slaves(row=new_y, column=new_x) if isinstance(sq, TetrominoSquare) and sq.status is SquareStatus.FALLING]
            except tk.TclError:
                continue

            # If there is a falling square
            if square:
                # Get just the square and not the list
                square = square[0]
                # Set the status to rotating to mark it as rotated. This keeps piece for being rotated more than once
                square.status = SquareStatus.ROTATING
                # Change square colour and redraw with new coordinates
                square.redraw(old_y, old_x)

        # After the rotation was successfully done graphically, rotate the internal squares matrix to reflect the new position
        if cw:
            self.squares = reverse_columns(transpose(self.squares))
        else:
            self.squares = reverse_rows(transpose(self.squares))

        # Rebuild internals
        self.squares_flat = [sq for sq in flatten(self.squares) if isinstance(sq, TetrominoSquare)]
        self.grid(min(x for x, _ in rotated_coords), min(y for _, y in rotated_coords))

        # Set the status of all the squares back to falling
        self.set_status(SquareStatus.FALLING)
        return True

class Tetris:
    ROWS = 24
    COLUMNS = 10
    SQUARE_SIZE = 32

    def __init__(self, parent):
        self.square_img = ImageTk.PhotoImage(Image.new('RGBA', (Tetris.SQUARE_SIZE, Tetris.SQUARE_SIZE), (255, 0, 0, 0)))
        self.parent = parent
        self.squares = [
            [
                tk.Label(parent, width=Tetris.SQUARE_SIZE, height=Tetris.SQUARE_SIZE, image=self.square_img, bd=0, bg='black')
                for f in range(Tetris.COLUMNS)
            ] for r in range(Tetris.ROWS)
        ]
        self.falling_tetromino = None
        self.has_lost = False

    def set_up_board(self):
        for rank in range(Tetris.ROWS):
            self.parent.grid_rowconfigure(rank, minsize=Tetris.SQUARE_SIZE)
        for file in range(Tetris.COLUMNS):
            self.parent.grid_columnconfigure(file, minsize=Tetris.SQUARE_SIZE)
        for rank in range(Tetris.ROWS):
            for file in range(Tetris.COLUMNS):
                square = self.squares[rank][file]
                square.grid(row=rank, column=file)

    def is_row_empty(self, row):
        return not any(isinstance(sq, TetrominoSquare) for sq in self.squares[row])

    def random_tetromino(self):
        if self.falling_tetromino or self.has_lost:
            return
        random_type = choice([t for t in TetrominoType])
        tetromino = Tetromino(self.parent, random_type)
        tetromino.grid(Tetris.COLUMNS//2, 0)
        for square in tetromino.squares_flat:
            row = square.grid_info()['row']
            col = square.grid_info()['column']
            if len(self.parent.grid_slaves(row, col)) > 2:
                self.has_lost = True
                return
        self.falling_tetromino = tetromino

    def tetromino_fall(self):
        if self.falling_tetromino is None:
            return
        fell = self.falling_tetromino.move_down()
        if not fell:
            self.falling_tetromino.set_status(SquareStatus.PLACED)
            self.falling_tetromino = None
            self.clear_lines()

    def tetromino_left(self):
        if self.falling_tetromino is None:
            return
        self.falling_tetromino.move_left()

    def tetromino_right(self):
        if self.falling_tetromino is None:
            return
        self.falling_tetromino.move_right()

    def tetromino_rotate(self, direction):
        if self.falling_tetromino is None:
            return
        if direction == 'ccw':
            rotated = self.falling_tetromino.rotate(False)
        elif direction == 'cw':
            rotated = self.falling_tetromino.rotate(True)

    def clear_lines(self):
        lines_to_clear = []
        for row in range(Tetris.ROWS):
            for col in range(Tetris.COLUMNS):
                square = self.parent.grid_slaves(row=row, column=col)[0]
                if not isinstance(square, TetrominoSquare):
                    break
            else:
                lines_to_clear.append(row)
        if not lines_to_clear:
            return
        for row in lines_to_clear:
            for col in range(Tetris.COLUMNS):
                square = self.parent.grid_slaves(row=row, column=col)[0]
                square.grid_forget()
        for line in lines_to_clear:
            for row in range(0, line):
                for col in range(Tetris.COLUMNS):
                    square = self.parent.grid_slaves(row=row, column=col)[0]
                    if isinstance(square, TetrominoSquare):
                        square.redraw(row + 1, col)


if __name__ == '__main__':
    root = tk.Tk()
    root.resizable(0,0)
    tetris_frame = tk.Frame(root, height=Tetris.SQUARE_SIZE*Tetris.ROWS, width=Tetris.SQUARE_SIZE*Tetris.COLUMNS)
    tetris_frame.grid_propagate(False)
    tetris = Tetris(tetris_frame)
    tetris.set_up_board()
    root.bind('<Return>', lambda *_: tetris.random_tetromino())
    root.bind('s', lambda *_: tetris.tetromino_fall())
    root.bind('a', lambda event: tetris.tetromino_left())
    root.bind('d', lambda event: tetris.tetromino_right())
    root.bind('z', lambda event: tetris.tetromino_rotate('ccw'))
    root.bind('x', lambda event: tetris.tetromino_rotate('cw'))
    tetris_frame.grid(row=0, column=0)
    root.mainloop()
