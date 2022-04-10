import tkinter as tk
from enum import Enum, auto
from PIL import Image, ImageTk
class Team(Enum):
    WHITE = auto()
    BLACK = auto()

class PieceImage(Enum):
    KING = Image.open('king_white.png'), Image.open('king_black.png')
    QUEEN = Image.open('queen_white.png'), Image.open('queen_black.png')
    ROOK = Image.open('rook_white.png'), Image.open('rook_black.png')
    BISHOP = Image.open('bishop_white.png'), Image.open('bishop_black.png')
    KNIGHT = Image.open('knight_white.png'), Image.open('knight_black.png')
    PAWN = Image.open('pawn_white.png'), Image.open('pawn_black.png')

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

    def move(self, new_rank, new_file):
        self.rank = new_rank
        self.file = new_file
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
        if self.team is Team.WHITE and new_rank == self.rank-1 and new_file == self.file:
            if self.chess_board.get_piece_at_pos(self.rank-1, self.file) is not None:
                return False
            return True
        if not self.has_moved and self.team is Team.WHITE and new_rank == self.rank-2 and new_file == self.file:
            if self.chess_board.get_piece_at_pos(self.rank-2, self.file) is not None:
                return False
            return True
        if self.team is Team.BLACK and new_rank==self.rank+1 and new_file==self.file:
            if self.chess_board.get_piece_at_pos(self.rank+1, self.file) is not None:
                return False
            return True
        if not self.has_moved and self.team is Team.BLACK and new_rank == self.rank+2 and new_file == self.file:
            if self.chess_board.get_piece_at_pos(self.rank+2, self.file) is not None:
                return False
            return True

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
        piece = piece_cls(self.parent, team, image, rank, file, square_colour, self)
        piece.bind('<Button-1>', lambda event, piece=piece: self.piece_click_handler(piece.mouse_click_handler(event)))
        piece.redraw()
        self.pieces.append(piece)

    def get_piece_at_pos(self, rank, file):
        objs = self.parent.grid_slaves(row=rank, column=file)
        for obj in objs:
            if isinstance(obj, Piece):
                return obj
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
        if self.selected_piece_pos is None:
            self.selected_piece_pos = position
        else:
            if self.get_piece_at_pos(*self.selected_piece_pos).team is self.get_piece_at_pos(*position).team:
                self.selected_piece_pos = position
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
        square_colour = self.squares[new_rank][new_file].cget('bg')
        can_move = piece.check_move(new_rank, new_file)
        if can_move:
            captured_piece = self.get_piece_at_pos(new_rank, new_file)
            piece.update_square_colour(square_colour)
            piece.move(new_rank, new_file)
            self.selected_piece_pos = None
            piece.has_moved = True
            if captured_piece is not None:
                captured_piece.capture()

            self.current_player = Team.WHITE if self.current_player is Team.BLACK else Team.BLACK
            check = self.is_checked()
            if not check:
                self.move_made = 'Success'
            else:
                self.move_made = 'Check'



    def is_checked(self):
        pieces_that_can_check = [piece for piece in self.pieces if piece.team is self.current_player and not piece.is_captured]
        king_that_can_be_checked = [piece for piece in self.pieces if piece.team is not self.current_player and isinstance(piece, King)][0]
        for piece in pieces_that_can_check:
            if piece.check_move(king_that_can_be_checked.rank, king_that_can_be_checked.file):
                # print('in check')
                return True
        return False

    def is_checkmate(self):
        ...

if __name__ == '__main__':
    root = tk.Tk()
    root.resizable(0, 0)
    chess_frame = tk.Frame(root, height=Chess.SQUARE_SIZE*Chess.RANKS, width=Chess.SQUARE_SIZE*Chess.FILES)
    chess_frame.grid_propagate(False)
    chess = Chess(chess_frame)
    chess.set_up_board()
    chess.create_classic_setup()
    chess_frame.grid(row=0, column=0)
    root.mainloop()