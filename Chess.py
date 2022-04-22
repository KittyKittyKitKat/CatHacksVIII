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
        self.in_future = False
        self.stored_pos = None
        super().__init__(parent, bd=0, width=Chess.SQUARE_SIZE, height=Chess.SQUARE_SIZE, bg=square_colour, image=self.tk_image)

    def check_move(self, new_rank, new_file):
        if new_rank == self.rank and new_file == self.file:
            return False
        occupying_piece = self.chess_board.get_piece_at_pos(new_rank, new_file)
        if occupying_piece is not None and occupying_piece.team is self.team:
            return False
        return True

    def move(self, new_rank, new_file):
        self.rank = new_rank
        self.file = new_file
        self.has_moved = True
        self.grid_forget()
        self.grid(row=self.rank, column=self.file)

    def premove(self, test_rank, test_file):
        self.stored_pos = self.rank, self.file
        self.rank = test_rank
        self.file = test_file

    def undo_premove(self):
        self.rank, self.file = self.stored_pos
        self.stored_pos = None

    def move_results_in_check(self, test_rank, test_file):
        if self.team is not self.chess_board.current_player:
            return False
        king = self.get_team_king()
        if king is None:
            return
        self.premove(test_rank, test_file)
        self.in_future = True
        would_be_check = False
        if king.is_checked():
            would_be_check = True
        self.in_future = False
        self.undo_premove()
        return would_be_check

    def square_is_valid_move(self, test_rank, test_file, occupying_piece):
        if isinstance(occupying_piece, King):
            return False
        would_be_check = self.move_results_in_check(test_rank, test_file)
        if occupying_piece is not None:
            if occupying_piece.team is self.team:
                return False
            occupying_piece.premove(-1, -1)
            would_be_check = self.move_results_in_check(test_rank, test_file)
            occupying_piece.undo_premove()
        if would_be_check:
            return False
        return True

    def get_direction_to_check(self, d_rank, d_file):
        if d_rank < 0 and d_file < 0:
            return -1, -1
        if d_rank < 0 and d_file > 0:
            return -1, 1
        if d_rank > 0 and d_file > 0:
            return 1, 1
        if d_rank > 0 and d_file < 0:
            return 1, -1
        if d_rank == 0 and d_file < 0:
            return 0, -1
        if d_rank == 0 and d_file > 0:
            return 0, 1
        if d_rank < 0 and d_file == 0:
            return -1, 0
        if d_rank > 0 and d_file == 0:
            return 1, 0

    def update_square_colour(self, new_square_colour):
        self.square_colour = new_square_colour
        self.config(bg=self.square_colour)

    def mouse_click_handler(self, event):
        return (self.rank, self.file)

    def capture(self):
        self.destroy()

    def get_team_king(self):
        for piece in self.chess_board.pieces:
            if isinstance(piece, King) and piece.team is self.team:
                return piece
        return None

    def __str__(self):
        return f'{self.team.name.title()} {self.__class__.__name__} at ({self.rank}, {self.file})'


class King(Piece):
    def check_move(self, new_rank, new_file):
        if new_rank == self.rank and new_file == self.file:
            return False
        dr, df = self.get_direction_to_check(new_rank - self.rank, new_file - self.file)
        occupying_piece = self.chess_board.get_piece_at_pos(new_rank, new_file)
        test_rank = self.rank + dr
        test_file = self.file + df
        if new_rank == test_rank and new_file == test_file:
            if self.in_check_at_square(test_rank, test_file):
                return False
            if occupying_piece is not None and occupying_piece.team is self.team:
                return False
            return True
        elif self.chess_board.get_piece_at_pos(test_rank, test_file) is not None:
            return False
        return False

    def in_check_at_square(self, test_rank, test_file):
        pieces_that_could_check = [piece for piece in self.chess_board.pieces if piece.team is not self.team]
        self.premove(-1, -1)
        in_check = False
        pieces_premoved = []
        for piece in pieces_that_could_check:
            piece_at = self.chess_board.get_piece_at_pos(test_rank, test_file)
            if piece_at is not None and piece_at.team is piece.team:
                piece_at.premove(-1, -1)
                pieces_premoved.append(piece_at)
            if piece.check_move(test_rank, test_file):
                in_check = True
                break
        self.undo_premove()
        for piece in pieces_premoved:
            piece.undo_premove()
        return in_check

    def is_checked(self):
        checked = self.in_check_at_square(self.rank, self.file)
        return checked


class Queen(Piece):
    def check_move(self, new_rank, new_file):
        if self.in_future:
            test_against_rank, test_against_file = self.stored_pos
        else:
            test_against_rank, test_against_file = self.rank, self.file
        if new_rank == test_against_rank and new_file == test_against_file:
            return False
        dr, df = self.get_direction_to_check(new_rank - test_against_rank, new_file - test_against_file)
        occupying_piece = self.chess_board.get_piece_at_pos(new_rank, new_file)
        for i in range(1, 8):
            test_rank = test_against_rank + i * dr
            test_file = test_against_file + i * df
            if new_rank == test_rank and new_file == test_file:
                return self.square_is_valid_move(test_rank, test_file, occupying_piece)
            elif self.chess_board.get_piece_at_pos(test_rank, test_file) is not None:
                return False
        return False


class Bishop(Piece):
    def check_move(self, new_rank, new_file):
        if self.in_future:
            test_against_rank, test_against_file = self.stored_pos
        else:
            test_against_rank, test_against_file = self.rank, self.file
        if new_rank == test_against_rank and new_file == test_against_file:
            return False
        dr, df = self.get_direction_to_check(new_rank - test_against_rank, new_file - test_against_file)
        occupying_piece = self.chess_board.get_piece_at_pos(new_rank, new_file)
        if abs(dr) != abs(df):
            return False
        for i in range(1, 8):
            test_rank = test_against_rank + i * dr
            test_file = test_against_file + i * df
            if new_rank == test_rank and new_file == test_file:
                return self.square_is_valid_move(test_rank, test_file, occupying_piece)
            elif self.chess_board.get_piece_at_pos(test_rank, test_file) is not None:
                return False
        return False


class Rook(Piece):
    def check_move(self, new_rank, new_file):
        if self.in_future:
            test_against_rank, test_against_file = self.stored_pos
        else:
            test_against_rank, test_against_file = self.rank, self.file
        if new_rank == test_against_rank and new_file == test_against_file:
            return False
        dr, df = self.get_direction_to_check(new_rank - test_against_rank, new_file - test_against_file)
        occupying_piece = self.chess_board.get_piece_at_pos(new_rank, new_file)
        if dr != 0 and df != 0:
            return False
        for i in range(1, 8):
            test_rank = test_against_rank + i * dr
            test_file = test_against_file + i * df
            if new_rank == test_rank and new_file == test_file:
                return self.square_is_valid_move(test_rank, test_file, occupying_piece)
            elif self.chess_board.get_piece_at_pos(test_rank, test_file) is not None:
                return False
        return False


class Knight(Piece):
    def check_move(self, new_rank,new_file):
        if self.in_future:
            test_against_rank, test_against_file = self.stored_pos
        else:
            test_against_rank, test_against_file = self.rank, self.file
        if new_rank == test_against_rank and new_file == test_against_file:
            return False
        occupying_piece = self.chess_board.get_piece_at_pos(new_rank, new_file)
        for dr in range(-2, 3):
            for df in range(-2, 3):
                if abs(dr) == abs(df):
                    continue
                if dr == 0 or df == 0:
                    continue
                test_rank = test_against_rank + dr
                test_file = test_against_file + df
                if new_rank == test_rank and new_file == test_file:
                   return self.square_is_valid_move(test_rank, test_file, occupying_piece)
        return False


class Pawn(Piece):
    def __init__(self, parent, team, image, rank, file, square_colour, chess_board):
        super(). __init__(parent, team, image, rank, file, square_colour, chess_board)
        self.has_just_moved_double = False

    def check_move(self, new_rank, new_file):
        if self.in_future:
            test_against_rank, test_against_file = self.stored_pos
        else:
            test_against_rank, test_against_file = self.rank, self.file
        if new_rank == test_against_rank and new_file == test_against_file:
            return False
        dr, df = self.get_direction_to_check(new_rank - test_against_rank, new_file - test_against_file)
        if (dr > 0 and self.team is Team.WHITE) or (dr < 0 and self.team is Team.BLACK):
            return False
        occupying_piece = self.chess_board.get_piece_at_pos(new_rank, new_file)
        if df == 0:
            for i in range(1, 3 if not self.has_moved else 2):
                test_rank = test_against_rank + i * dr
                test_file = test_against_file + i * df
                if new_rank == test_rank and new_file == test_file:
                    if occupying_piece is not None:
                        return False
                    self.has_just_moved_double = i == 2
                    if self.move_results_in_check(test_rank, test_file):
                        return False
                    return True
                elif self.chess_board.get_piece_at_pos(test_rank, test_file) is not None:
                    return False
        elif abs(dr) == 1:
            test_rank = test_against_rank + dr
            test_file = test_against_file + df
            if test_rank == new_rank and test_file == new_file:
                if occupying_piece is not None and occupying_piece.team is not self.team:
                    return True
                elif self.move_results_in_check(test_rank, test_file):
                    return False
                elif occupying_piece is None:
                    en_passant_pawn = self.chess_board.get_piece_at_pos(test_against_rank, test_file)
                    if isinstance(en_passant_pawn, Pawn) and en_passant_pawn.has_just_moved_double and en_passant_pawn.team is not self.team:
                        self.chess_board.pawn_captured_en_passant = en_passant_pawn
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
        self.pawn_captured_en_passant = None

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
        piece.move(rank, file)
        piece.has_moved = False
        self.pieces.append(piece)

    def get_piece_at_pos(self, rank, file):
        for piece in self.pieces:
            if piece.rank == rank and piece.file == file:
                return piece
        return None

    def create_classic_setup(self):
        for file in range(Chess.FILES):
            self.create_piece(Chess.RANKS-2, file, Pawn, Team.WHITE)
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

        self.create_piece(Chess.RANKS-1, Chess.FILES-5, Queen, Team.WHITE)
        self.create_piece(0, Chess.FILES-5, Queen, Team.BLACK)

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
        piece = self.get_piece_at_pos(*position)
        # assert piece is not None
        if self.selected_piece_pos is None:
            if piece.team is self.current_player:
                self.selected_piece_pos = position
                self.highlight_available_moves()
        else:
            if self.selected_piece_pos == position:
                self.selected_piece_pos = None
                self.reset_board_colouring()
            elif self.get_piece_at_pos(*self.selected_piece_pos).team is piece.team:
                self.selected_piece_pos = position
                self.highlight_available_moves()
            else:
                self.move_piece(*position)

    def change_player(self, override=None):
        if override is not None:
            self.current_player = override
        else:
            self.current_player = Team.WHITE if self.current_player is Team.BLACK else Team.BLACK

    def move_piece(self, new_rank, new_file):
        piece_to_move = self.get_piece_at_pos(*self.selected_piece_pos)
        can_move = piece_to_move.check_move(new_rank, new_file)
        if piece_to_move is None:
            return
        if piece_to_move.team is not self.current_player:
            self.selected_piece_pos = None
            return
        if can_move:
            self.reset_board_colouring()
            for pawn in [piece for piece in self.pieces if isinstance(piece, Pawn)]:
                if pawn is not piece_to_move:
                    pawn.has_just_moved_double = False
            captured_piece = self.get_piece_at_pos(new_rank, new_file)
            square_colour = self.squares[new_rank][new_file].cget('bg')
            piece_to_move.update_square_colour(square_colour)
            piece_to_move.move(new_rank, new_file)
            self.selected_piece_pos = None
            if captured_piece is not None:
                captured_piece.capture()
                self.pieces.remove(captured_piece)
            if self.pawn_captured_en_passant is not None:
                self.pawn_captured_en_passant.capture()
                self.pieces.remove(self.pawn_captured_en_passant)
                self.pawn_captured_en_passant = None
            self.change_player()

    def highlight_available_moves(self):
        if self.selected_piece_pos is None:
            return
        piece_clicked = self.get_piece_at_pos(*self.selected_piece_pos)
        if piece_clicked.team is not self.current_player:
            return
        if piece_clicked.square_colour == Chess.LIGHT_COLOUR:
            piece_clicked.update_square_colour(Chess.HIGHLIGHT_LIGHT_COLOUR)
        if piece_clicked.square_colour == Chess.DARK_COLOUR:
            piece_clicked.update_square_colour(Chess.HIGHLIGHT_DARK_COLOUR)
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


if __name__ == '__main__':
    root = tk.Tk()
    root.resizable(0, 0)
    root.title('Chess')
    chess_frame = tk.Frame(root, height=Chess.SQUARE_SIZE*Chess.RANKS, width=Chess.SQUARE_SIZE*Chess.FILES)
    chess_frame.grid_propagate(False)
    chess = Chess(chess_frame)
    chess.set_up_board()
    chess.create_classic_setup()
    root.bind("<Return>", lambda *_: chess.change_player())
    chess_frame.grid(row=0, column=0)
    root.mainloop()