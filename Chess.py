import tkinter as tk
from enum import Enum, auto
from PIL import Image, ImageTk
from abc import ABC, abstractmethod

PLACEHOLDER_IMG_WHITE = Image.new('RGBA', (16, 16), '#ffffff')
PLACEHOLDER_IMG_BLACK = Image.new('RGBA', (16, 16), '#000000')

class Team(Enum):
    WHITE = auto()
    BLACK = auto()

class PieceImage(Enum):
    KING = PLACEHOLDER_IMG_WHITE, PLACEHOLDER_IMG_BLACK
    QUEEN = PLACEHOLDER_IMG_WHITE, PLACEHOLDER_IMG_BLACK
    ROOK = PLACEHOLDER_IMG_WHITE, PLACEHOLDER_IMG_BLACK
    BISHOP = PLACEHOLDER_IMG_WHITE, PLACEHOLDER_IMG_BLACK
    KNIGHT = PLACEHOLDER_IMG_WHITE, PLACEHOLDER_IMG_BLACK
    PAWN = PLACEHOLDER_IMG_WHITE, PLACEHOLDER_IMG_BLACK

class Piece(ABC):
    @abstractmethod
    def __init__(self, parent, team, image, rank, file, square_colour):
        ...

    @abstractmethod
    def move(self, new_rank, new_file):
        ...

    def update_square_colour(self, new_square_colour):
        self.square_colour = new_square_colour
        self.config(bg=self.square_colour)

    def redraw(self):
        self.grid_forget()
        self.grid(row=self.rank, column=self.file)

    def mouse_click_handler(self, event):
        return (self.rank, self.file)

class King(tk.Label, Piece):
    def __init__(self, parent, team, image, rank, file, square_colour):
        self.parent = parent
        self.team = team
        self.image = image
        self.tk_image = ImageTk.PhotoImage(image)
        self.rank = rank
        self.file = file
        self.square_colour = square_colour
        super().__init__(parent, bd=0, width=Chess.SQUARE_SIZE, height=Chess.SQUARE_SIZE, bg=square_colour, image=self.tk_image)

class Queen(tk.Label, Piece):
    def __init__(self, parent, team, image, rank, file, square_colour):
        self.parent = parent
        self.team = team
        self.image = image
        self.tk_image = ImageTk.PhotoImage(image)
        self.rank = rank
        self.file = file
        self.square_colour = square_colour
        super().__init__(parent, bd=0, width=Chess.SQUARE_SIZE, height=Chess.SQUARE_SIZE, bg=square_colour, image=self.tk_image)

class Bishop(tk.Label, Piece):
    def __init__(self, parent, team, image, rank, file, square_colour):
        self.parent = parent
        self.team = team
        self.image = image
        self.tk_image = ImageTk.PhotoImage(image)
        self.rank = rank
        self.file = file
        self.square_colour = square_colour
        super().__init__(parent, bd=0, width=Chess.SQUARE_SIZE, height=Chess.SQUARE_SIZE, bg=square_colour, image=self.tk_image)

class Rook(tk.Label, Piece):
    def __init__(self, parent, team, image, rank, file, square_colour):
        self.parent = parent
        self.team = team
        self.image = image
        self.tk_image = ImageTk.PhotoImage(image)
        self.rank = rank
        self.file = file
        self.square_colour = square_colour
        super().__init__(parent, bd=0, width=Chess.SQUARE_SIZE, height=Chess.SQUARE_SIZE, bg=square_colour, image=self.tk_image)

class Knight(tk.Label, Piece):
    def __init__(self, parent, team, image, rank, file, square_colour):
        self.parent = parent
        self.team = team
        self.image = image
        self.tk_image = ImageTk.PhotoImage(image)
        self.rank = rank
        self.file = file
        self.square_colour = square_colour
        super().__init__(parent, bd=0, width=Chess.SQUARE_SIZE, height=Chess.SQUARE_SIZE, bg=square_colour, image=self.tk_image)

class Pawn(tk.Label, Piece):
    def __init__(self, parent, team, image, rank, file, square_colour):
        self.parent = parent
        self.team = team
        self.image = image
        self.tk_image = ImageTk.PhotoImage(image)
        self.rank = rank
        self.file = file
        self.square_colour = square_colour
        super().__init__(parent, bd=0, width=Chess.SQUARE_SIZE, height=Chess.SQUARE_SIZE, bg=square_colour, image=self.tk_image)

    def move(self, new_rank, new_file):
        """self.rank = new_rank
        self.file = new_file
        return True"""



class Chess:
    RANKS = 8
    FILES = 8
    SQUARE_SIZE = 64
    LIGHT_COLOUR = '#f0ab51'
    DARK_COLOUR = '#613d0e'

    def __init__(self, parent):
        self.square_img = ImageTk.PhotoImage(Image.new('RGBA', (Chess.SQUARE_SIZE, Chess.SQUARE_SIZE), (255, 0, 0, 0)))
        self.parent = parent
        self.squares = [
            [
                tk.Label(parent, width=Chess.SQUARE_SIZE, height=Chess.SQUARE_SIZE, bd=0, image=self.square_img) for f in range(Chess.FILES)
            ] for r in range(Chess.RANKS)
        ]
        self.current_player = Team.WHITE
        self.selected_piece_pos = None

    def set_up_board(self):
        for rank in range(self.RANKS):
            self.parent.grid_rowconfigure(rank, minsize=Chess.SQUARE_SIZE)
        for file in range(self.FILES):
            self.parent.grid_columnconfigure(file, minsize=Chess.SQUARE_SIZE)
        for rank in range(self.RANKS):
            light = not (rank % 2)
            for file in range(self.FILES):
                square = self.squares[rank][file]
                square.config(bg=Chess.LIGHT_COLOUR if light else Chess.DARK_COLOUR)
                square.bind('<Button-1>', self.square_click_handler)
                square.grid(row=rank, column=file)
                light = not light

    def create_piece(self, rank, file, piece_cls, team):
        images = PieceImage[piece_cls.__name__.upper()].value
        image = images[0] if team is Team.WHITE else images[1]
        square_colour = self.squares[rank][file].cget('bg')
        piece = piece_cls(self.parent, team, image, rank, file, square_colour)
        piece.bind('<Button-1>', lambda event, piece=piece: self.piece_click_handler(piece.mouse_click_handler(event)))
        piece.redraw()

    def get_piece_at_pos(self, rank, file):
        objs = self.parent.grid_slaves(row=rank, column=file)
        for obj in objs:
            if isinstance(obj, Piece):
                return obj
        return None

    def create_classic_setup(self):
        #TODO: Add remaining pieces
        white_pawn_rank = self.squares[-2]
        for file, _ in enumerate(white_pawn_rank):
            self.create_piece(Chess.RANKS-2, file, Pawn, Team.WHITE)
        black_pawn_rank = self.squares[1]
        for file, _ in enumerate(black_pawn_rank):
            self.create_piece(1, file, Pawn, Team.BLACK)

    def square_click_handler(self, event):
        if self.selected_piece_pos is None:
            return
        x = event.x_root - self.parent.winfo_rootx()
        y = event.y_root - self.parent.winfo_rooty()
        rank = (y // Chess.SQUARE_SIZE) % 8
        file = (x // Chess.SQUARE_SIZE) % 8
        self.move_piece(rank, file)

    def piece_click_handler(self, position):
        self.selected_piece_pos = position

    def move_piece(self, new_rank, new_file):
        piece = self.get_piece_at_pos(*self.selected_piece_pos)
        if piece is None:
            return
        square_colour = self.squares[new_rank][new_file].cget('bg')
        moved_successfully = piece.move(new_rank, new_file)
        if moved_successfully:
            piece.update_square_colour(square_colour)
            piece.redraw()


if __name__ == '__main__':
    root = tk.Tk()
    root.resizable(0,0)
    chess_frame = tk.Frame(root, height=Chess.SQUARE_SIZE*Chess.RANKS, width=Chess.SQUARE_SIZE*Chess.FILES)
    chess_frame.grid_propagate(False)
    chess = Chess(chess_frame)
    chess.set_up_board()
    # chess.create_classic_setup()
    chess.create_piece(rank=3, file=2, piece_cls=Pawn, team=Team.WHITE)
    chess_frame.grid(row=0, column=0)
    root.mainloop()