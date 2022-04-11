import tkinter as tk
from enum import Enum, auto
from PIL import Image, ImageTk

class Team(Enum):
    WHITE = auto()
    BLACK = auto()


class PieceImage(Enum):
    KING = Image.open('assets/king_white.png'), Image.open('assets/king_black.png')
    QUEEN = Image.open('assets/queen_white.png'), Image.open('assets/queen_black.png')
    ROOK = Image.open('assets/rook_white.png'), Image.open('assets/rook_black.png')
    BISHOP = Image.open('assets/bishop_white.png'), Image.open('assets/bishop_black.png')
    KNIGHT = Image.open('assets/knight_white.png'), Image.open('assets/knight_black.png')
    PAWN = Image.open('assets/pawn_white.png'), Image.open('assets/pawn_black.png')


class Piece(tk.Label):
    def __init__(self, parent, team, image, rank, file, square_colour, chess_board):
        self.parent = parent
        self.team = team
        self.image = image
        self.tk_image = ImageTk.PhotoImage(image)
        self.rank = rank
        self.file = file
        self.square_colour = square_colour
        self.chess_board = chess_board
        self.has_moved = False
        self.is_captured = False
        super().__init__(parent, bd=0, width=Chess.SQUARE_SIZE, height=Chess.SQUARE_SIZE, bg=square_colour, image=self.tk_image)

    def check_move(self, new_rank, new_file):
        return True

    def move(self, new_rank, new_file):
        self.rank = new_rank
        self.file = new_file
        self.has_moved = True
        self.redraw()

    def update_square_colour(self, new_square_colour):
        self.square_colour = new_square_colour
        self.config(bg=self.square_colour)

    def redraw(self):
        self.grid_forget()
        self.grid(row=self.rank, column=self.file)

    def mouse_click_handler(self, event):
        return (self.rank, self.file)

    def capture(self):
        self.is_captured = True
        self.grid_forget()

    def __str__(self):
        return self.team.name +" " + self.__class__.__name__


class King(Piece):
    def check_move(self, new_rank, new_file):
        if new_rank == self.rank and new_file == self.file:
            return False
        dr = new_rank - self.rank
        df = new_file - self.file
        if abs(dr) == abs(df):
            if dr < 0 and df < 0:
                test_rank = self.rank - 1
                test_file = self.file - 1
                if self.chess_board.is_valid_coordinate (test_rank, test_file) == True:
                    if new_rank == test_rank and new_file == test_file:
                        occupying_piece = self.chess_board.get_piece_at_pos(new_rank, new_file)
                        if occupying_piece is not None and occupying_piece.team is self.team:
                            return False
                        return True
                    elif self.chess_board.get_piece_at_pos(test_rank, test_file) is not None:
                        return False
            if dr < 0 and df > 0:
                test_rank = self.rank - 1
                test_file = self.file + 1
                if self.chess_board.is_valid_coordinate(test_rank, test_file) == True:
                    if new_rank == test_rank and new_file == test_file:
                        occupying_piece = self.chess_board.get_piece_at_pos(new_rank, new_file)
                        if occupying_piece is not None and occupying_piece.team is self.team:
                            return False
                        return True
                    elif self.chess_board.get_piece_at_pos(test_rank, test_file) is not None:
                        return False
            if dr > 0 and df > 0:
                test_rank = self.rank + 1
                test_file = self.file + 1
                if self.chess_board.is_valid_coordinate(test_rank, test_file) == True:
                    if new_rank == test_rank and new_file == test_file:
                        occupying_piece = self.chess_board.get_piece_at_pos(new_rank, new_file)
                        if occupying_piece is not None and occupying_piece.team is self.team:
                            return False
                        return True
                    elif self.chess_board.get_piece_at_pos(test_rank, test_file) is not None:
                        return False
            if dr > 0 and df < 0:
                test_rank = self.rank + 1
                test_file = self.file - 1
                if self.chess_board.is_valid_coordinate(test_rank, test_file) == True:
                    if new_rank == test_rank and new_file == test_file:
                        occupying_piece = self.chess_board.get_piece_at_pos(new_rank, new_file)
                        if occupying_piece is not None and occupying_piece.team is self.team:
                            return False
                        return True
                    elif self.chess_board.get_piece_at_pos(test_rank, test_file) is not None:
                        return False
        if dr == 0 or df == 0:
            if dr == 0 and df < 0:
                test_file = self.file - 1
                if self.chess_board.is_valid_coordinate(self.rank, test_file) == True:
                    if new_file == test_file:
                        occupying_piece = self.chess_board.get_piece_at_pos(self.rank, new_file)
                        if occupying_piece is not None and occupying_piece.team is self.team:
                            return False
                        return True
                    elif self.chess_board.get_piece_at_pos(self.rank, test_file) is not None:
                        return False
            if dr == 0 and df > 0:
                test_file = self.file + 1
                if self.chess_board.is_valid_coordinate(self.rank, test_file) == True:
                    if new_file == test_file:
                        occupying_piece = self.chess_board.get_piece_at_pos(self.rank, new_file)
                        if occupying_piece is not None and occupying_piece.team is self.team:
                            return False
                        return True
                    elif self.chess_board.get_piece_at_pos(self.rank, test_file) is not None:
                        return False
            if dr < 0 and df == 0:
                test_rank = self.rank - 1
                if self.chess_board.is_valid_coordinate(test_rank, self.file) == True:
                    if new_rank == test_rank:
                        occupying_piece = self.chess_board.get_piece_at_pos(new_rank, self.file)
                        if occupying_piece is not None and occupying_piece.team is self.team:
                            return False
                        return True
                    elif self.chess_board.get_piece_at_pos(test_rank, self.file) is not None:
                        return False
            if dr > 0 and df == 0:
                test_rank = self.rank + 1
                if self.chess_board.is_valid_coordinate(test_rank, self.file) == True:
                    if new_rank == test_rank:
                        occupying_piece = self.chess_board.get_piece_at_pos(new_rank, self.file)
                        if occupying_piece is not None and occupying_piece.team is self.team:
                            return False
                        return True
                    elif self.chess_board.get_piece_at_pos(test_rank, self.file) is not None:
                        return False


class Queen(Piece):
    def check_move(self, new_rank, new_file):
        if new_rank == self.rank and new_file == self.file:
            return False
        dr = new_rank - self.rank
        df = new_file - self.file
        if abs(dr) == abs(df):
            if dr < 0 and df < 0:
                stop = min(self.rank, self.file)
                for i in range(1, stop + 1):
                    test_rank = self.rank - i
                    test_file = self.file - i
                    if new_rank == test_rank and new_file == test_file:
                        occupying_piece = self.chess_board.get_piece_at_pos(new_rank, new_file)
                        if occupying_piece is not None and occupying_piece.team is self.team:
                            return False
                        return True
                    elif self.chess_board.get_piece_at_pos(test_rank, test_file) is not None:
                        return False
            if dr < 0 and df > 0:
                stop = min(self.rank, Chess.FILES - self.file)
                for i in range(1, stop + 1):
                    test_rank = self.rank - i
                    test_file = self.file + i
                    if new_rank == test_rank and new_file == test_file:
                        occupying_piece = self.chess_board.get_piece_at_pos(new_rank, new_file)
                        if occupying_piece is not None and occupying_piece.team is self.team:
                            return False
                        return True
                    elif self.chess_board.get_piece_at_pos(test_rank, test_file) is not None:
                        return False
            if dr > 0 and df > 0:
                stop = min(Chess.RANKS - self.rank, Chess.FILES - self.file)
                for i in range(1, stop + 1):
                    test_rank = self.rank + i
                    test_file = self.file + i
                    if new_rank == test_rank and new_file == test_file:
                        occupying_piece = self.chess_board.get_piece_at_pos(new_rank, new_file)
                        if occupying_piece is not None and occupying_piece.team is self.team:
                            return False
                        return True
                    elif self.chess_board.get_piece_at_pos(test_rank, test_file) is not None:
                        return False
            if dr > 0 and df < 0:
                stop = min(Chess.RANKS - self.rank, self.file)
                for i in range(1, stop + 1):
                    test_rank = self.rank + i
                    test_file = self.file - i
                    if new_rank == test_rank and new_file == test_file:
                        occupying_piece = self.chess_board.get_piece_at_pos(new_rank, new_file)
                        if occupying_piece is not None and occupying_piece.team is self.team:
                            return False
                        return True
                    elif self.chess_board.get_piece_at_pos(test_rank, test_file) is not None:
                        return False
        if dr == 0 or df == 0:
            if dr == 0 and df < 0:
                for i in range(1, self.file + 1):
                    test_file = self.file - i
                    if new_file == test_file:
                        occupying_piece = self.chess_board.get_piece_at_pos(self.rank, new_file)
                        if occupying_piece is not None and occupying_piece.team is self.team:
                            return False
                        return True
                    elif self.chess_board.get_piece_at_pos(self.rank, test_file) is not None:
                        return False
            if dr == 0 and df > 0:
                for i in range(1, Chess.FILES - self.file):
                    test_file = self.file + i
                    if new_file == test_file:
                        occupying_piece = self.chess_board.get_piece_at_pos(self.rank, new_file)
                        if occupying_piece is not None and occupying_piece.team is self.team:
                            return False
                        return True
                    elif self.chess_board.get_piece_at_pos(self.rank, test_file) is not None:
                        return False
            if dr < 0 and df == 0:
                for i in range(1, self.rank + 1):
                    test_rank = self.rank - i
                    if new_rank == test_rank:
                        occupying_piece = self.chess_board.get_piece_at_pos(new_rank, self.file)
                        if occupying_piece is not None and occupying_piece.team is self.team:
                            return False
                        return True
                    elif self.chess_board.get_piece_at_pos(test_rank, self.file) is not None:
                        return False
            if dr > 0 and df == 0:
                for i in range(1, Chess.RANKS - self.rank):
                    test_rank = self.rank + i
                    if new_rank == test_rank:
                        occupying_piece = self.chess_board.get_piece_at_pos(new_rank, self.file)
                        if occupying_piece is not None and occupying_piece.team is self.team:
                            return False
                        return True
                    elif self.chess_board.get_piece_at_pos(test_rank, self.file) is not None:
                        return False


class Bishop(Piece):
    def check_move(self, new_rank, new_file):
        if new_rank == self.rank and new_file == self.file:
            return False
        dr = new_rank - self.rank
        df = new_file - self.file
        if abs(dr) == abs(df):
            if dr < 0 and df < 0:
                stop = min(self.rank, self.file)
                for i in range(1, stop + 1):
                    test_rank = self.rank - i
                    test_file = self.file - i
                    if new_rank == test_rank and new_file == test_file:
                        occupying_piece = self.chess_board.get_piece_at_pos(new_rank, new_file)
                        if occupying_piece is not None and occupying_piece.team is self.team:
                            return False
                        return True
                    elif self.chess_board.get_piece_at_pos(test_rank, test_file) is not None:
                        return False
            if dr < 0 and df > 0:
                stop = min(self.rank, Chess.FILES - self.file)
                for i in range(1, stop + 1):
                    test_rank = self.rank - i
                    test_file = self.file + i
                    if new_rank == test_rank and new_file == test_file:
                        occupying_piece = self.chess_board.get_piece_at_pos(new_rank, new_file)
                        if occupying_piece is not None and occupying_piece.team is self.team:
                            return False
                        return True
                    elif self.chess_board.get_piece_at_pos(test_rank, test_file) is not None:
                        return False
            if dr > 0 and df > 0:
                stop = min(Chess.RANKS - self.rank, Chess.FILES - self.file)
                for i in range(1, stop + 1):
                    test_rank = self.rank + i
                    test_file = self.file + i
                    if new_rank == test_rank and new_file == test_file:
                        occupying_piece = self.chess_board.get_piece_at_pos(new_rank, new_file)
                        if occupying_piece is not None and occupying_piece.team is self.team:
                            return False
                        return True
                    elif self.chess_board.get_piece_at_pos(test_rank, test_file) is not None:
                        return False
            if dr > 0 and df < 0:
                stop = min(Chess.RANKS - self.rank, self.file)
                for i in range(1, stop + 1):
                    test_rank = self.rank + i
                    test_file = self.file - i
                    if new_rank == test_rank and new_file == test_file:
                        occupying_piece = self.chess_board.get_piece_at_pos(new_rank, new_file)
                        if occupying_piece is not None and occupying_piece.team is self.team:
                            return False
                        return True
                    elif self.chess_board.get_piece_at_pos(test_rank, test_file) is not None:
                        return False


class Rook(Piece):
    def check_move(self, new_rank, new_file):
        if new_rank == self.rank and new_file == self.file:
            return False
        dr = new_rank - self.rank
        df = new_file - self.file
        if dr == 0 or df == 0:
            if dr == 0 and df < 0:
                for i in range(1, self.file + 1):
                    test_file = self.file - i
                    if new_file == test_file:
                        occupying_piece = self.chess_board.get_piece_at_pos(self.rank, new_file)
                        if occupying_piece is not None and occupying_piece.team is self.team:
                            return False
                        return True
                    elif self.chess_board.get_piece_at_pos(self.rank, test_file) is not None:
                        return False
            if dr == 0 and df > 0:
                for i in range(1, Chess.FILES - self.file):
                    test_file = self.file + i
                    if new_file == test_file:
                        occupying_piece = self.chess_board.get_piece_at_pos(self.rank, new_file)
                        if occupying_piece is not None and occupying_piece.team is self.team:
                            return False
                        return True
                    elif self.chess_board.get_piece_at_pos(self.rank, test_file) is not None:
                        return False
            if dr < 0 and df == 0:
                for i in range(1, self.rank + 1):
                    test_rank = self.rank - i
                    if new_rank == test_rank:
                        occupying_piece = self.chess_board.get_piece_at_pos(new_rank, self.file)
                        if occupying_piece is not None and occupying_piece.team is self.team:
                            return False
                        return True
                    elif self.chess_board.get_piece_at_pos(test_rank, self.file) is not None:
                        return False
            if dr > 0 and df == 0:
                for i in range(1, Chess.RANKS - self.rank):
                    test_rank = self.rank + i
                    if new_rank == test_rank:
                        occupying_piece = self.chess_board.get_piece_at_pos(new_rank, self.file)
                        if occupying_piece is not None and occupying_piece.team is self.team:
                            return False
                        return True
                    elif self.chess_board.get_piece_at_pos(test_rank, self.file) is not None:
                        return False


class Knight(Piece):
    def check_move(self, new_rank,new_file):
        occupying_piece = self.chess_board.get_piece_at_pos(new_rank, new_file)
        if new_rank == self.rank - 2 and new_file == self.file + 1:
            if occupying_piece is not None and occupying_piece.team is self.team:
                return False
            return True
        if new_rank == self.rank - 2 and new_file == self.file - 1:
            if occupying_piece is not None and occupying_piece.team is self.team:
                return False
            return True
        if new_rank == self.rank + 2 and new_file == self.file + 1:
            if occupying_piece is not None and occupying_piece.team is self.team:
                return False
            return True
        if new_rank == self.rank + 2 and new_file == self.file - 1:
            if occupying_piece is not None and occupying_piece.team is self.team:
                return False
            return True
        if new_rank == self.rank - 1 and new_file == self.file + 2:
            if occupying_piece is not None and occupying_piece.team is self.team:
                return False
            return True
        if new_rank == self.rank - 1 and new_file == self.file - 2:
            if occupying_piece is not None and occupying_piece.team is self.team:
                return False
            return True
        if new_rank == self.rank + 1 and new_file == self.file + 2:
            if occupying_piece is not None and occupying_piece.team is self.team:
                return False
            return True
        if new_rank == self.rank + 1 and new_file == self.file - 2:
            if occupying_piece is not None and occupying_piece.team is self.team:
                return False
            return True


class Pawn(Piece):
    def check_move(self, new_rank, new_file):
        if new_rank == self.rank and new_file == self.file:
            return False
        for dr in range(-2, 3):
            for df in range(-1, 2):
                if abs(dr) != 1 and abs(df) == 1:
                    continue
                if dr > 0 and self.team is not Team.BLACK:
                    continue
                if dr < 0 and self.team is not Team.WHITE:
                    continue
                if abs(dr) == 2 and self.has_moved:
                    continue
                test_rank = self.rank + dr
                test_file = self.file + df
                if test_rank == new_rank and test_file == new_file:
                    if abs(dr) ==1 and abs(df) == 1:
                        if self.chess_board.get_piece_at_pos(test_rank, test_file) is None:
                            return False
                    return True

        return False


class Chess:
    RANKS = 8
    FILES = 8
    SQUARE_SIZE = 64
    LIGHT_COLOUR = '#f0ab51'
    DARK_COLOUR = '#613d0e'
    HIGHLIGHT_LIGHT_COLOUR = '#56f051'
    HIGHLIGHT_DARK_COLOUR = '#0b8017'

    def __init__(self, parent):
        self.square_img = ImageTk.PhotoImage(Image.new('RGBA', (Chess.SQUARE_SIZE, Chess.SQUARE_SIZE), (255, 0, 0, 0)))
        self.parent = parent
        self.squares = [
            [
                tk.Label(parent, width=Chess.SQUARE_SIZE, height=Chess.SQUARE_SIZE, bd=0, image=self.square_img) for f in range(Chess.FILES)
            ] for r in range(Chess.RANKS)
        ]
        self.pieces = []
        self.current_player = Team.WHITE
        self.selected_piece_pos = None
        self.locked = False
        self.move_made = None

    def set_up_board(self):
        for rank in range(self.RANKS):
            self.parent.grid_rowconfigure(rank, minsize=Chess.SQUARE_SIZE)
        for file in range(self.FILES):
            self.parent.grid_columnconfigure(file, minsize=Chess.SQUARE_SIZE)
        for rank in range(self.RANKS):
            for file in range(self.FILES):
                square = self.squares[rank][file]
                square.bind('<Button-1>', self.square_click_handler)
                square.grid(row=rank, column=file)
        self.reset_board_colouring()

    def reset_board_colouring(self):
        for rank in range(self.RANKS):
            light = not (rank % 2)
            for file in range(self.FILES):
                colour = Chess.LIGHT_COLOUR if light else Chess.DARK_COLOUR
                square = self.squares[rank][file]
                square.config(bg=colour)
                light = not light
                piece = self.get_piece_at_pos(rank, file)
                if piece is not None:
                    piece.update_square_colour(colour)

    def create_piece(self, rank, file, piece_cls, team):
        images = PieceImage[piece_cls.__name__.upper()].value
        image = images[0] if team is Team.WHITE else images[1]
        square_colour = self.squares[rank][file].cget('bg')
        piece = piece_cls(self.parent, team, image, rank, file, square_colour, self)
        piece.bind('<Button-1>', lambda event, piece=piece: self.piece_click_handler(piece.mouse_click_handler(event)))
        piece.redraw()
        self.pieces.append(piece)

    def get_piece_at_pos(self, rank, file):
        for piece in self.pieces:
            if piece.rank == rank and piece.file == file:
                return piece
        return None

    def is_valid_coordinate(self, rank, file):
        return rank in range(len(self.squares)) and file in range(len(self.squares[0]))

    def create_classic_setup(self):
        white_pawn_rank = self.squares[-2]
        for file, _ in enumerate(white_pawn_rank):
            self.create_piece(Chess.RANKS-2, file, Pawn, Team.WHITE)
        black_pawn_rank = self.squares[1]
        for file, _ in enumerate(black_pawn_rank):
            self.create_piece(1, file, Pawn, Team.BLACK)

        self.create_piece(Chess.RANKS-1, Chess.FILES-1, Rook, Team.WHITE)
        self.create_piece(Chess.RANKS-1, 0, Rook, Team.WHITE)
        self.create_piece(0,Chess.FILES-1, Rook, Team.BLACK)
        self.create_piece(0,0, Rook, Team.BLACK)

        self.create_piece(Chess.RANKS-1, Chess.FILES-2, Knight, Team.WHITE)
        self.create_piece(Chess.RANKS-1, 1, Knight, Team.WHITE)
        self.create_piece(0, Chess.FILES-2, Knight, Team.BLACK)
        self.create_piece(0, 1, Knight, Team.BLACK)

        self.create_piece(Chess.RANKS-1,Chess.FILES-3, Bishop, Team.WHITE)
        self.create_piece(Chess.RANKS-1, 2, Bishop, Team.WHITE)
        self.create_piece(0, Chess.FILES-3, Bishop, Team.BLACK)
        self.create_piece(0, 2, Bishop, Team.BLACK)

        self.create_piece(Chess.RANKS-1, Chess.FILES-4, King, Team.WHITE)
        self.create_piece(0, Chess.FILES-4, King, Team.BLACK)

        self.create_piece (Chess.RANKS-1, Chess.FILES-5, Queen, Team.WHITE)
        self.create_piece (0, Chess.FILES-5, Queen, Team.BLACK )

    def square_click_handler(self, event):
        if self.selected_piece_pos is None or self.locked:
            return
        x = event.x_root - self.parent.winfo_rootx()
        y = event.y_root - self.parent.winfo_rooty()
        rank = (y // Chess.SQUARE_SIZE) % 8
        file = (x // Chess.SQUARE_SIZE) % 8
        self.move_piece(rank, file)

    def piece_click_handler(self, position):
        if self.locked:
            return
        self.reset_board_colouring()
        if self.selected_piece_pos is None:
            if (piece := self.get_piece_at_pos(*position)) is not None and piece.team is not self.current_player:
                return
            self.selected_piece_pos = position
            self.highlight_available_moves()
        elif self.selected_piece_pos == position:
            self.selected_piece_pos = None
        elif self.get_piece_at_pos(*self.selected_piece_pos).team is self.get_piece_at_pos(*position).team:
            self.selected_piece_pos = position
            self.highlight_available_moves()
        else:
            self.move_piece(*position)

    def move_piece(self, new_rank, new_file):
        self.move_made = None
        piece = self.get_piece_at_pos(*self.selected_piece_pos)
        if piece is None:
            return
        if piece.team is not self.current_player:
            self.selected_piece_pos = None
            return
        can_move = piece.check_move(new_rank, new_file)
        if can_move:
            self.reset_board_colouring()
            captured_piece = self.get_piece_at_pos(new_rank, new_file)
            square_colour = self.squares[new_rank][new_file].cget('bg')
            piece.update_square_colour(square_colour)
            piece.move(new_rank, new_file)
            self.selected_piece_pos = None
            if captured_piece is not None:
                captured_piece.capture()
            self.current_player = Team.WHITE if self.current_player is Team.BLACK else Team.BLACK
            check = self.is_checked()
            if not check:
                self.move_made = 'Success'
            else:
                self.move_made = 'Check'

    def highlight_available_moves(self):
        if self.selected_piece_pos is None:
            return
        piece_clicked = self.get_piece_at_pos(*self.selected_piece_pos)
        if piece_clicked.team is not self.current_player:
            return
        for r in range(Chess.RANKS):
            for f in range(Chess.FILES):
                if piece_clicked.check_move(r, f):
                    square = self.squares[r][f]
                    if square.cget('bg') == Chess.LIGHT_COLOUR:
                        square.config(bg=Chess.HIGHLIGHT_LIGHT_COLOUR)
                    if square.cget('bg') == Chess.DARK_COLOUR:
                        square.config(bg=Chess.HIGHLIGHT_DARK_COLOUR)
                    piece = self.get_piece_at_pos(r, f)
                    if piece is not None:
                        if piece.square_colour == Chess.LIGHT_COLOUR:
                            piece.update_square_colour(Chess.HIGHLIGHT_LIGHT_COLOUR)
                        if piece.square_colour == Chess.DARK_COLOUR:
                            piece.update_square_colour(Chess.HIGHLIGHT_DARK_COLOUR)

    def is_checked(self):
        pieces_that_can_check = [piece for piece in self.pieces if piece.team is self.current_player and not piece.is_captured]
        king_that_can_be_checked = [piece for piece in self.pieces if piece.team is not self.current_player and isinstance(piece, King)]
        if not king_that_can_be_checked:
            return False
        king = king_that_can_be_checked[0]
        for piece in pieces_that_can_check:
            if piece.check_move(king.rank, king.file):
                print('in check')
                return True
        return False

    def is_checkmate(self):
        ...


if __name__ == '__main__':
    root = tk.Tk()
    root.resizable(0, 0)
    root.title('Chess')
    chess_frame = tk.Frame(root, height=Chess.SQUARE_SIZE*Chess.RANKS, width=Chess.SQUARE_SIZE*Chess.FILES)
    chess_frame.grid_propagate(False)
    chess = Chess(chess_frame)
    chess.set_up_board()
    chess.create_classic_setup()
    chess_frame.grid(row=0, column=0)
    root.mainloop()