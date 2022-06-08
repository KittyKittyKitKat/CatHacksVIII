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
    RESIGNED = auto()


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
                    if piece.file != test_file:
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
        self.chess_board.pawn_captured_en_passant = None
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
        return False


class Square(tk.Label):
    SQUARE_SIZE = 64

    def __init__(self, parent, background_image, rank, file):
        self.parent = parent
        self.rank = rank
        self.file = file
        self.occupying_piece = None
        self.background_image = background_image
        self.highlight_colour = None
        self.tk_image = ImageTk.PhotoImage(self.background_image)
        super().__init__(parent, width=Square.SQUARE_SIZE, height=Square.SQUARE_SIZE, bd=0, image=self.tk_image)

    def add_text(self, rank, file, chess_board):
        fnt = ImageFont.truetype('assets/Rubik-Medium.ttf', 13)
        new_bg = self.background_image.copy()
        d = ImageDraw.Draw(new_bg)

        if self.background_image is chess_board.LIGHT_SQUARE_IMAGE:
            font_colour = chess_board.DARK_SQUARE_IMAGE.copy().convert('RGB').resize((1, 1), resample=0).getpixel((0, 0))
        elif self.background_image is chess_board.DARK_SQUARE_IMAGE:
            font_colour = chess_board.LIGHT_SQUARE_IMAGE.copy().convert('RGB').resize((1, 1), resample=0).getpixel((0, 0))

        if file == 0:
            d.text((2, 0), f'{Chess.RANKS - rank}', font=fnt, fill=font_colour)

        if rank == Chess.RANKS-1:
            d.text((Square.SQUARE_SIZE-9, Square.SQUARE_SIZE-16), chr(97+file), font=fnt, fill=font_colour)

        self.background_image = new_bg
        self.tk_image = ImageTk.PhotoImage(self.background_image)
        self.config(image=self.tk_image)

    def highlight(self, colour_rgb):
        self.highlight_colour = colour_rgb
        highlighted = ImageOps.colorize(
            ImageOps.grayscale(self.background_image),
            black=tuple(int(.3 * c) for c in colour_rgb),
            white=tuple(min(c+100, 255) for c in colour_rgb)
        )
        self.tk_image = ImageTk.PhotoImage(highlighted)
        if self.occupying_piece is None:
            self.config(image=self.tk_image)
        else:
            self.place_piece(self.occupying_piece)

    def remove_highlight(self):
        self.highlight_colour = None
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
    BORDER_WIDTH=2

    def __init__(self, parent, square_sheet, flip_after_move):
        self.parent = parent
        self.squares = []
        self.pieces = []
        self.current_player = Team.WHITE
        self.flip_after_move = flip_after_move
        self.board_flipped = False
        self.selected_piece = None
        self.pawn_captured_en_passant = None
        self.castling_rook = None
        self.game_state = GameState.PLAYING
        self.highlight_move_colour = (0, 255, 0)
        self.highlight_check_colour = (255, 0, 0)
        self.texts = {}
        spritesheet = Image.open(square_sheet)
        self.LIGHT_SQUARE_IMAGE = spritesheet.crop((0, 0, 64, 64))
        self.DARK_SQUARE_IMAGE = spritesheet.crop((64, 0, 128, 64))
        self.font_colour = self.DARK_SQUARE_IMAGE.copy().convert('RGB').resize((1, 1), resample=0).getpixel((0, 0))
        self.bg_colour = self.LIGHT_SQUARE_IMAGE.copy().convert('RGB').resize((1, 1), resample=0).getpixel((0, 0))
        self._config_widgets()
        self.set_up_board()
        self.create_classic_setup()

    def _config_widgets(self):
        self.parent.grid_propagate(False)
        self.parent.config(
            height=Square.SQUARE_SIZE*Chess.RANKS,
            width=Square.SQUARE_SIZE*Chess.FILES
        )

    def _make_text_label(self, parent, text, font_size):
        if text not in self.texts:
            fnt = ImageFont.truetype('assets/Rubik-Medium.ttf', font_size)
            size = fnt.getsize(text)
            text_img = Image.new('RGBA', size, self.bg_colour)
            d = ImageDraw.Draw(text_img, 'RGBA')
            d.text((0, 0), text, font=fnt, fill=self.font_colour)
            text_tk = ImageTk.PhotoImage(text_img)
            self.texts[text] = text_tk
        else:
            text_tk = self.texts[text]
        text_label = tk.Label(parent, bd=0, image=text_tk)
        return text_label

    def set_up_board(self):
        for rank in range(self.RANKS):
            light = not (rank % 2)
            row = []
            for file in range(self.FILES):
                colour = self.LIGHT_SQUARE_IMAGE if light else self.DARK_SQUARE_IMAGE
                square = Square(self.parent, colour, rank, file)
                square.add_text(rank, file, self)
                light = not light
                square.bind('<Button-1>', self.click_handler)
                square.grid(row=rank, column=file)
                row.append(square)
            self.squares.append(row)

    def reset_board_colouring(self):
        for rank in self.squares:
            for square in rank:
                square.remove_highlight()

    def create_piece(self, rank, file, piece_cls, team):
        images = PieceImage[piece_cls.__name__.upper()].value
        image = images[0] if team is Team.WHITE else images[1]
        piece = piece_cls(self.parent, team, image, rank, file, self)
        square = self.squares[rank][file]
        square.place_piece(piece)
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
        if self.board_flipped:
            self.flip_board()

    def flip_board(self):
        if not self.flip_after_move:
            return
        self.board_flipped = not self.board_flipped
        for rank in self.squares:
            for square in rank:
                internal_pos = square.rank, square.file
                grid_pos = square.grid_info()['row'], square.grid_info()['column']
                if internal_pos == grid_pos:
                    square.grid(row=Chess.RANKS-square.rank-1, column=Chess.FILES-square.file-1)
                else:
                    square.grid(row=square.rank, column=square.file)

    def click_handler(self, event):
        if self.game_state is not GameState.PLAYING:
            return
        x = event.x_root - self.parent.winfo_rootx()
        y = event.y_root - self.parent.winfo_rooty()
        rank = (y // Square.SQUARE_SIZE) % 8
        file = (x // Square.SQUARE_SIZE) % 8
        if self.board_flipped:
            rank = Chess.RANKS - rank - 1
            file = Chess.FILES - file - 1
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
            self.move_piece(piece_to_move, new_rank, new_file)
            if isinstance(piece_to_move, Pawn):
                if self.pawn_captured_en_passant is not None:
                    self.capture_piece(self.pawn_captured_en_passant)
                    self.pawn_captured_en_passant = None
                if new_rank == 0 or new_rank == Chess.RANKS - 1:
                    self.promote_piece(piece_to_move)
            self.change_player()
            self.highlight_check()
            over = self.is_game_over()
            if not over:
                self.flip_board()

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

    def promote_piece(self, piece):
        self.grey_out_board()
        parent_root = self.parent.winfo_toplevel()
        promote_root = tk.Toplevel()
        promote_root.resizable(0, 0)
        promote_root.wm_attributes('-type', 'splash')
        promotion_frame = tk.Frame(
            promote_root,
            height=Square.SQUARE_SIZE + 2 * self.BORDER_WIDTH,
            width=Square.SQUARE_SIZE*4 + 2 * self.BORDER_WIDTH,
            highlightthickness=self.BORDER_WIDTH,
            highlightbackground='white'
        )
        squares = []
        piece_index = {
            0: Queen,
            1: Rook,
            2: Knight,
            3: Bishop
        }

        def sync_windows(event=None):
            promote_root_x = parent_root.winfo_x() + parent_root.winfo_width()//4
            promote_root_y = parent_root.winfo_y() + parent_root.winfo_height()//2 - Square.SQUARE_SIZE//2
            promote_root.geometry(f'+{promote_root_x}+{promote_root_y}')

        def hover_handler(event):
            x = event.x_root - promotion_frame.winfo_rootx()
            y = event.y_root - promotion_frame.winfo_rooty()
            if x not in range(Square.SQUARE_SIZE*4+1):
                return
            if y not in range(Square.SQUARE_SIZE+1):
                return
            file = (x // Square.SQUARE_SIZE) % 4
            for square in squares:
                square.remove_highlight()
            squares[file].highlight(self.highlight_move_colour)

        def click_handler(square):
            parent_root.unbind('<Configure>')
            promotion = piece_index[squares.index(square)]
            self.capture_piece(piece)
            self.create_piece(piece.rank, piece.file, promotion, piece.team)
            promote_root.grab_release()
            promote_root.destroy()
            for rank in self.squares:
                for board_square in rank:
                    board_square.remove_highlight()

        for i in range(4):
            colour = self.DARK_SQUARE_IMAGE if i % 2 else self.LIGHT_SQUARE_IMAGE
            square = Square(promotion_frame, colour)
            piece_cls = piece_index[i]
            images = PieceImage[piece_cls.__name__.upper()].value
            image = images[0] if piece.team is Team.WHITE else images[1]
            square_piece = piece_cls(promotion_frame, piece.team, image, 0, 0, None)
            square.place_piece(square_piece)
            square.bind('<Button-1>',lambda e, square=square: click_handler(square))
            square.grid(row=0, column=i)
            squares.append(square)

        promotion_frame.grid(row=0, column=0)
        promote_root.bind('<Motion>', hover_handler)
        promote_root.wait_visibility()
        promote_root.grab_set()
        promote_root.transient(parent_root)
        sync_windows()
        parent_root.bind('<Configure>', sync_windows)

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

    def grey_out_board(self):
        for rank in self.squares:
            for board_square in rank:
                board_square.highlight((150, 150, 150))

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
            else:
                self.game_state = GameState.STALEMATE
        if self.game_state not in (GameState.PLAYING, GameState.PAUSED):
            self.game_over_screen()
            return True
        return False

    def game_over_screen(self):
        parent_root = self.parent.winfo_toplevel()
        game_over_root = tk.Toplevel()
        game_over_root.resizable(0, 0)
        game_over_root.wm_attributes('-type', 'splash')
        border_colour = '#'+''.join('{:02X}'.format(c) for c in self.font_colour)
        bg_colour = '#'+''.join('{:02X}'.format(c) for c in self.bg_colour)
        self.change_player()
        match self.game_state:
            case GameState.CHECKMATE:
                text = f'Checkmate: {self.current_player.name.title()} wins'
            case GameState.STALEMATE:
                text = 'Draw: Stalemate'
        game_over_frame = tk.Frame(
            game_over_root,
            bg=bg_colour,
            highlightthickness=self.BORDER_WIDTH,
            highlightbackground=border_colour
        )
        game_over_text = self._make_text_label(game_over_frame, text, 20)
        play_again_text = self._make_text_label(game_over_frame, 'Play Again?', 18)
        play_again_text_height = int(parent_root.call(play_again_text.cget('image'), 'cget', '-height'))
        play_again_text_width = int(parent_root.call(play_again_text.cget('image'), 'cget', '-width'))
        play_again_button = tk.Button(
            game_over_frame,
            bg=bg_colour,
            height=play_again_text_height+8,
            width=play_again_text_width+8,
            image=play_again_text.cget('image'),
            bd=0,
            highlightthickness=self.BORDER_WIDTH,
            highlightbackground=border_colour
        )

        def sync_windows(event=None):
            game_over_root_x = parent_root.winfo_x() + (parent_root.winfo_width() - game_over_root.winfo_width())//2
            game_over_root_y = parent_root.winfo_y() + (parent_root.winfo_height() - game_over_root.winfo_height())//2
            game_over_root.geometry(f'+{game_over_root_x}+{game_over_root_y}')

        def play_again_callback():
            parent_root.unbind('<Configure>')
            game_over_root.grab_release()
            game_over_root.destroy()
            self.reset_classic_setup()

        play_again_button.config(command=play_again_callback)
        game_over_text.grid(row=0, column=0, pady=10, padx=10)
        play_again_button.grid(row=1, column=0, pady=10, padx=10)
        game_over_frame.grid(row=0, column=0)
        game_over_root.wait_visibility()
        game_over_root.grab_set()
        game_over_root.transient(parent_root)
        sync_windows()
        parent_root.bind('<Configure>', sync_windows)


if __name__ == '__main__':
    root = tk.Tk()
    root.resizable(0, 0)
    root.title('Chess')
    chess_frame = tk.Frame(root)
    chess = Chess(chess_frame, 'assets/chess/squares.png', False)
    # Debug, remember to remove
    # root.bind('<Return>', lambda *_: chess.change_player())
    # root.bind('<Control-r>', lambda *_: chess.reset_classic_setup())
    chess_frame.grid(row=0, column=0)
    root.mainloop()