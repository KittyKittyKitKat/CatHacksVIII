import tkinter as tk
from enum import Enum, auto
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageTk

class Team(Enum):
    WHITE = auto()
    BLACK = auto()


class GameState(Enum):
    PLAYING = auto()
    PAUSED = auto()
    CHECKMATE = auto()
    STALEMATE = auto()
    INSUFFICIENT_MATERIAL = auto()
    DEAD_STATE = auto()
    THREEFOLD_REPETITION = auto()
    FIFTY_MOVE = auto()
    MUTUAL_DRAW = auto()


class PieceImage(Enum):
    KING = Image.open('assets/chess/king_white.png'), Image.open('assets/chess/king_black.png')
    QUEEN = Image.open('assets/chess/queen_white.png'), Image.open('assets/chess/queen_black.png')
    ROOK = Image.open('assets/chess/rook_white.png'), Image.open('assets/chess/rook_black.png')
    BISHOP = Image.open('assets/chess/bishop_white.png'), Image.open('assets/chess/bishop_black.png')
    KNIGHT = Image.open('assets/chess/knight_white.png'), Image.open('assets/chess/knight_black.png')
    PAWN = Image.open('assets/chess/pawn_white.png'), Image.open('assets/chess/pawn_black.png')


class Piece:
    def __init__(self, parent, team, image, rank, file, chess_board):
        self.parent = parent
        self.team = team
        self.image = image
        self.rank = rank
        self.file = file
        self.chess_board = chess_board
        self.has_moved = False
        self.in_future = False
        self.stored_pos = None

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

    def premove(self, rank, file):
        if not self.in_future:
            self.stored_pos = self.rank, self.file
            self.rank = rank
            self.file = file
            self.in_future = True

    def undo_premove(self):
        if self.in_future:
            self.rank, self.file = self.stored_pos
            self.stored_pos = None
            self.in_future = False

    def move_results_in_check(self, test_rank, test_file):
        if self.team is not self.chess_board.current_player:
            return False
        king = self.get_team_king()
        if king is None:
            return
        self.premove(test_rank, test_file)
        would_be_check = False
        if king.is_checked():
            would_be_check = True
        self.undo_premove()
        return would_be_check

    def square_is_valid_move(self, test_rank, test_file, occupying_piece):
        if isinstance(occupying_piece, King):
            return False
        would_be_check = self.move_results_in_check(test_rank, test_file)
        if occupying_piece is not None:
            if occupying_piece.team is self.team:
                return False
            self.chess_board.pieces.remove(occupying_piece)
            would_be_check = self.move_results_in_check(test_rank, test_file)
            self.chess_board.pieces.append(occupying_piece)
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

    def mouse_click_handler(self, event):
        return (self.rank, self.file)

    def get_team_king(self):
        for piece in self.chess_board.pieces:
            if isinstance(piece, King) and piece.team is self.team:
                return piece
        return None

    def __str__(self):
        return f'{self.team.name.title()} {self.__class__.__name__} at ({self.rank}, {self.file})'


class King(Piece):
    def __init__(self, parent, team, image, rank, file, chess_board):
        super(). __init__(parent, team, image, rank, file, chess_board)
        self.has_just_castled = False

    def check_move(self, new_rank, new_file, check_check=True):
        if new_rank == self.rank and new_file == self.file:
            return False
        dr, df = self.get_direction_to_check(new_rank - self.rank, new_file - self.file)
        occupying_piece = self.chess_board.get_piece_at_pos(new_rank, new_file)
        if isinstance(occupying_piece, King):
            return False
        team_rooks = [
            piece for piece in self.chess_board.pieces
            if isinstance(piece, Rook) and piece.team is self.team
        ]
        can_try_castling = (
            not self.has_moved and
            not dr and
            any(filter(lambda p: not p.has_moved, team_rooks)) and
            not (check_check and self.is_checked())
        )
        for i in range(1, 3 if can_try_castling else 2):
            test_rank = self.rank + i * dr
            test_file = self.file + i * df
            if check_check and self.in_check_at_square(test_rank, test_file):
                return False
            if new_rank == test_rank and new_file == test_file:
                if occupying_piece is not None and occupying_piece.team is self.team:
                    return False
                if i == 2:
                    self.chess_board.castling_rook = None
                    for rook in team_rooks:
                        if not rook.has_moved:
                            if rook.file < self.file and df == -1:
                                self.chess_board.castling_rook = rook
                            elif rook.file > self.file and df == 1:
                                self.chess_board.castling_rook = rook
                            continue
                        if rook.file > self.file and df != -1:
                            return False
                        if rook.file < self.file and df != 1:
                            return False
                    self.has_just_castled = True
                return True
            elif self.chess_board.get_piece_at_pos(test_rank, test_file) is not None:
                return False
        return False

    def in_check_at_square(self, test_rank, test_file):
        self.chess_board.pieces.remove(self)
        in_check = False
        pieces_that_could_check = [piece for piece in self.chess_board.pieces if piece.team is not self.team]
        piece_at = self.chess_board.get_piece_at_pos(test_rank, test_file)
        for piece in pieces_that_could_check:
            if piece_at is not None:
                self.chess_board.pieces.remove(piece_at)
            if isinstance(piece, King):
                if piece.check_move(test_rank, test_file, check_check=False):
                    in_check = True
            elif isinstance(piece, Pawn):
                if piece.check_move(test_rank, test_file, check_check=True):
                    in_check = True
            elif piece.check_move(test_rank, test_file):
                in_check = True
            if piece_at is not None:
                self.chess_board.pieces.append(piece_at)
            if in_check:
                break
        self.chess_board.pieces.append(self)
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
    def __init__(self, parent, team, image, rank, file, chess_board):
        super(). __init__(parent, team, image, rank, file, chess_board)
        self.has_just_moved_double = False

    def check_move(self, new_rank, new_file, check_check=False):
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
                if (occupying_piece is not None and occupying_piece.team is not self.team) or check_check:
                    return True
                elif self.move_results_in_check(test_rank, test_file):
                    return False
                elif occupying_piece is None:
                    en_passant_pawn = self.chess_board.get_piece_at_pos(test_against_rank, test_file)
                    if isinstance(en_passant_pawn, Pawn) and en_passant_pawn.has_just_moved_double and en_passant_pawn.team is not self.team:
                        self.chess_board.pawn_captured_en_passant = en_passant_pawn
                        return True
                    else:
                        self.chess_board.pawn_captured_en_passant = None
        return False


class Square(tk.Label):
    SQUARE_SIZE = 64

    def __init__(self, parent, rank, file, chess_board, background_image):
        self.parent = parent
        self.rank = rank
        self.file = file
        self.needs_text = (rank == Chess.RANKS-1 or file == 0)
        self.chess_board = chess_board
        self.width = Square.SQUARE_SIZE
        self.height = Square.SQUARE_SIZE
        self.occupying_piece = None
        self.background_image = background_image
        self.piece = None
        self.tk_image = ImageTk.PhotoImage(self.background_image)
        super().__init__(parent, width=Square.SQUARE_SIZE, height=Square.SQUARE_SIZE, bd=0, image=self.tk_image)

    def change_background_image(self, new_background_image):
        self.background_image = new_background_image
        self.tk_image = ImageTk.PhotoImage(self.background_image)
        if self.occupying_piece is None:
            self.config(image=self.tk_image)
        else:
            self.place_piece(self.occupying_piece)

    def highlight(self, colour_rgb):
        highlighted = ImageOps.colorize(
            ImageOps.grayscale(self.background_image),
            black=(0,0,0),
            white=(255, 255, 255),
            mid=colour_rgb
        )
        self.tk_image = ImageTk.PhotoImage(highlighted)
        if self.occupying_piece is None:
            self.config(image=self.tk_image)
        else:
            self.place_piece(self.occupying_piece)

    def remove_highlight(self):
        self.tk_image = ImageTk.PhotoImage(self.background_image)
        if self.occupying_piece is None:
            self.config(image=self.tk_image)
        else:
            self.place_piece(self.occupying_piece)

    def place_piece(self, piece):
        self.occupying_piece = piece
        piece_image = piece.image
        composite = ImageTk.getimage(self.tk_image).copy()
        composite.paste(piece_image, (2, 2), piece_image)
        self.tk_image = ImageTk.PhotoImage(composite)
        self.config(image=self.tk_image)

    def remove_piece(self):
        self.occupying_piece = None
        self.tk_image = ImageTk.PhotoImage(self.background_image)
        self.config(image=self.tk_image)


class Chess:
    RANKS = 8
    FILES = 8

    def __init__(self, parent, square_sheet):
        self.parent = parent
        square_img = Image.new('RGBA', (Square.SQUARE_SIZE, Square.SQUARE_SIZE), (255, 0, 0, 0))
        self.squares = [[Square(parent, r, f, self, square_img) for f in range(Chess.FILES)] for r in range(Chess.RANKS)]
        self.pieces = []
        self.current_player = Team.WHITE
        self.selected_piece = None
        self.pawn_captured_en_passant = None
        self.castling_rook = None
        self.game_state = GameState.PLAYING
        self.highlight_move_colour = (0, 255, 0)
        self.highlight_check_colour = (255, 0, 0)
        spritesheet = Image.open(square_sheet)
        self.LIGHT_SQUARE_IMAGE = spritesheet.crop((0, 0, 64, 64))
        self.DARK_SQUARE_IMAGE = spritesheet.crop((64, 0, 128, 64))

    def set_up_board(self):
        for rank in range(self.RANKS):
            self.parent.grid_rowconfigure(rank, minsize=Square.SQUARE_SIZE)
        for file in range(self.FILES):
            self.parent.grid_columnconfigure(file, minsize=Square.SQUARE_SIZE)
        for rank in range(self.RANKS):
            light = not (rank % 2)
            for file in range(self.FILES):
                colour = self.LIGHT_SQUARE_IMAGE if light else self.DARK_SQUARE_IMAGE
                square = self.squares[rank][file]
                square.change_background_image(colour)
                light = not light
                square.bind('<Button-1>', self.click_handler)
                square.grid(row=rank, column=file)

    def reset_board_colouring(self):
        for rank in self.squares:
            for square in rank:
                square.remove_highlight()

    def create_piece(self, rank, file, piece_cls, team):
        images = PieceImage[piece_cls.__name__.upper()].value
        image = images[0] if team is Team.WHITE else images[1]
        piece = piece_cls(self.parent, team, image, rank, file, self)
        piece.move(rank, file)
        square = self.squares[rank][file]
        square.place_piece(piece)
        piece.has_moved = False
        self.pieces.append(piece)

    def get_piece_at_pos(self, rank, file):
        for piece in self.pieces:
            if piece.rank == rank and piece.file == file:
                return piece
        return None

    def get_current_king(self):
        try:
            king = [piece for piece in self.pieces if isinstance(piece, King) and piece.team is self.current_player][0]
        except IndexError:
            return None
        else:
            return king

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

    def reset_classic_setup(self):
        self.reset_board_colouring()
        while self.pieces:
            piece = self.pieces[0]
            self.capture_piece(piece)
        self.create_classic_setup()
        self.current_player = Team.WHITE
        self.game_state = GameState.PLAYING
        self.selected_piece = None
        self.pawn_captured_en_passant = None
        self.castling_rook = None

    def click_handler(self, event):
        if self.game_state is not GameState.PLAYING:
            return
        x = event.x_root - self.parent.winfo_rootx()
        y = event.y_root - self.parent.winfo_rooty()
        rank = (y // Square.SQUARE_SIZE) % 8
        file = (x // Square.SQUARE_SIZE) % 8
        square_clicked = self.squares[rank][file]

        if self.selected_piece is None:
            if square_clicked.occupying_piece is not None:
                if square_clicked.occupying_piece.team is not self.current_player:
                    return
                self.selected_piece = square_clicked.occupying_piece
                self.reset_board_colouring()
                self.highlight_available_moves()
                self.highlight_check()
        else:
            if square_clicked.occupying_piece is not None:
                if square_clicked.occupying_piece is self.selected_piece:
                    self.reset_board_colouring()
                    self.highlight_check()
                    self.selected_piece = None
                    return
                if square_clicked.occupying_piece.team is self.selected_piece.team:
                    self.selected_piece = square_clicked.occupying_piece
                    self.reset_board_colouring()
                    self.highlight_available_moves()
                    self.highlight_check()
                    return
            self.player_move(rank, file)

    def change_player(self, override=None):
        if override is not None:
            self.current_player = override
        else:
            self.current_player = Team.WHITE if self.current_player is Team.BLACK else Team.BLACK

    def player_move(self, new_rank, new_file):
        piece_to_move = self.selected_piece
        can_move = piece_to_move.check_move(new_rank, new_file)
        if can_move:
            self.reset_board_colouring()
            for pawn in [piece for piece in self.pieces if isinstance(piece, Pawn)]:
                if pawn is not piece_to_move:
                    pawn.has_just_moved_double = False
            if isinstance(piece_to_move, King) and piece_to_move.has_just_castled:
                df = 1 if self.castling_rook.file < piece_to_move.file else -1
                self.move_piece(self.castling_rook, new_rank, new_file + df)
                self.castling_rook = None
            self.selected_piece = None
            captured_piece = self.get_piece_at_pos(new_rank, new_file)
            if captured_piece is not None:
                self.capture_piece(captured_piece)
            if isinstance(piece_to_move, Pawn) and self.pawn_captured_en_passant is not None:
                self.capture_piece(self.pawn_captured_en_passant)
                self.pawn_captured_en_passant = None
            self.move_piece(piece_to_move, new_rank, new_file)
            self.change_player()
            self.highlight_check()
            self.is_game_over()

    def move_piece(self, piece, new_rank, new_file):
        current_square = self.squares[piece.rank][piece.file]
        current_square.remove_piece()
        new_square = self.squares[new_rank][new_file]
        new_square.place_piece(piece)
        piece.move(new_rank, new_file)

    def capture_piece(self, piece):
        current_square = self.squares[piece.rank][piece.file]
        current_square.remove_piece()
        self.pieces.remove(piece)

    def highlight_available_moves(self):
        if self.selected_piece is None:
            return
        if self.selected_piece.team is not self.current_player:
            return
        for r in range(Chess.RANKS):
            for f in range(Chess.FILES):
                if self.selected_piece.check_move(r, f) or (self.selected_piece.rank == r and self.selected_piece.file == f):
                    square = self.squares[r][f]
                    square.highlight(self.highlight_move_colour)

    def highlight_check(self):
        king = self.get_current_king()
        if king is not None:
            if king.is_checked():
                king_square = self.squares[king.rank][king.file]
                king_square.highlight(self.highlight_check_colour)

    def is_game_over(self):
        if (king := self.get_current_king()) is None:
            return
        king_pieces = [piece for piece in self.pieces if piece.team is king.team]
        any_piece_can_move = False
        for piece in king_pieces:
            for rank in range(Chess.RANKS):
                for file in range(Chess.FILES):
                    if piece.check_move(rank, file):
                        any_piece_can_move = True
                        break
        if not any_piece_can_move:
            if king.is_checked():
                self.game_state = GameState.CHECKMATE
                print('checkmate')
            else:
                self.game_state = GameState.STALEMATE
                print('stalemate')


if __name__ == '__main__':
    root = tk.Tk()
    root.resizable(0, 0)
    root.title('Chess')
    chess_frame = tk.Frame(root, height=Square.SQUARE_SIZE*Chess.RANKS, width=Square.SQUARE_SIZE*Chess.FILES)
    chess_frame.grid_propagate(False)
    chess = Chess(chess_frame, 'assets/chess/squares.png')
    chess.set_up_board()
    chess.create_classic_setup()
    # Debug, remember to remove
    # root.bind('<Return>', lambda *_: chess.change_player())
    # root.bind('<Control-r>', lambda *_: chess.reset_classic_setup())
    chess_frame.grid(row=0, column=0)
    root.mainloop()