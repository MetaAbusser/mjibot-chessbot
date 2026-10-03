import chess
import numpy as np
import numpy.ma as ma

piece_value = {
    chess.PAWN: 100,
    chess.KNIGHT: 300,
    chess.BISHOP: 300,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 0  # this is pointless as the king can never be captured
}

# following values are from https://www.chessprogramming.org/PeSTO%27s_Evaluation_Function
# sorry for the formatting, pycharm really doesn't like multiple spaces

# tables for mid game:

mg_pawn_table = np.array([
    0, 0, 0, 0, 0, 0, 0, 0,
    98, 134, 61, 95, 68, 126, 34, -11,
    -6, 7, 26, 31, 65, 56, 25, -20,
    -14, 13, 6, 21, 23, 12, 17, -23,
    -27, -2, -5, 12, 17, 6, 10, -25,
    -26, -4, -4, -10, 3, 3, 33, -12,
    -35, -1, -20, -23, -15, 24, 38, -22,
    0, 0, 0, 0, 0, 0, 0, 0
])

mg_knight_table = np.array([
    -167, -89, -34, -49, 61, -97, -15, -107,
    -73, -41, 72, 36, 23, 62, 7, -17,
    -47, 60, 37, 65, 84, 129, 73, 44,
    -9, 17, 19, 53, 37, 69, 18, 22,
    -13, 4, 16, 13, 28, 19, 21, -8,
    -23, -9, 12, 10, 19, 17, 25, -16,
    -29, -53, -12, -3, -1, 18, -14, -19,
    -105, -21, -58, -33, -17, -28, -19, -23
])

mg_bishop_table = np.array([
    -29, 4, -82, -37, -25, -42, 7, -8,
    -26, 16, -18, -13, 30, 59, 18, -47,
    -16, 37, 43, 40, 35, 50, 37, -2,
    -4, 5, 19, 50, 37, 37, 7, -2,
    -6, 13, 13, 26, 34, 12, 10, 4,
    0, 15, 15, 15, 14, 27, 18, 10,
    4, 15, 16, 0, 7, 21, 33, 1,
    -33, -3, -14, -21, -13, -12, -39, -21
])

mg_rook_table = np.array([
    32, 42, 32, 51, 63, 9, 31, 43,
    27, 32, 58, 62, 80, 67, 26, 44,
    -5, 19, 26, 36, 17, 45, 61, 16,
    -24, -11, 7, 26, 24, 35, -8, -20,
    -36, -26, -12, -1, 9, -7, 6, -23,
    -45, -25, -16, -17, 3, 0, -5, -33,
    -44, -16, -20, -9, -1, 11, -6, -71,
    -19, -13, 1, 17, 16, 7, -37, -26
])

mg_queen_table = np.array([
    -28, 0, 29, 12, 59, 44, 43, 45,
    -24, -39, -5, 1, -16, 57, 28, 54,
    -13, -17, 7, 8, 29, 56, 47, 57,
    -27, -27, -16, -16, -1, 17, -2, 1,
    -9, -26, -9, -10, -2, -4, 3, -3,
    -14, 2, -11, -2, -5, 2, 14, 5,
    -35, -8, 11, 2, 8, 15, -3, 1,
    -1, -18, -9, 10, -15, -25, -31, -50
])

mg_king_table = np.array([
    -65, 23, 16, -15, -56, -34, 2, 13,
    29, -1, -20, -7, -8, -4, -38, -29,
    -9, 24, 2, -16, -20, 6, 22, -22,
    -17, -20, -12, -27, -30, -25, -14, -36,
    -49, -1, -27, -39, -46, -44, -33, -51,
    -14, -14, -22, -46, -44, -30, -15, -27,
    1, 7, -8, -64, -43, -16, 9, 8,
    -15, 36, 12, -54, 8, -28, 24, 14
])

# tables for end game:

eg_pawn_table = np.array([
    0, 0, 0, 0, 0, 0, 0, 0,
    178, 173, 158, 134, 147, 132, 165, 187,
    94, 100, 85, 67, 56, 53, 82, 84,
    32, 24, 13, 5, -2, 4, 17, 17,
    13, 9, -3, -7, -7, -8, 3, -1,
    4, 7, -6, 1, 0, -5, -1, -8,
    13, 8, 8, 10, 13, 0, 2, -7,
    0, 0, 0, 0, 0, 0, 0, 0
])

eg_knight_table = np.array([
    -58, -38, -13, -28, -31, -27, -63, -99,
    -25, -8, -25, -2, -9, -25, -24, -52,
    -24, -20, 10, 9, -1, -9, -19, -41,
    -17, 3, 22, 22, 22, 11, 8, -18,
    -18, -6, 16, 25, 16, 17, 4, -18,
    -23, -3, -1, 15, 10, -3, -20, -22,
    -42, -20, -10, -5, -2, -20, -23, -44,
    -29, -51, -23, -15, -22, -18, -50, -64
])

eg_bishop_table = np.array([
    -14, -21, -11, -8, -7, -9, -17, -24,
    -8, -4, 7, -12, -3, -13, -4, -14,
    2, -8, 0, -1, -2, 6, 0, 4,
    -3, 9, 12, 9, 14, 10, 3, 2,
    -6, 3, 13, 19, 7, 10, -3, -9,
    -12, -3, 8, 10, 13, 3, -7, -15,
    -14, -18, -7, -1, 4, -9, -15, -27,
    -23, -9, -23, -5, -9, -16, -5, -17
])

eg_rook_table = np.array([
    13, 10, 18, 15, 12, 12, 8, 5,
    11, 13, 13, 11, -3, 3, 8, 3,
    7, 7, 7, 5, 4, -3, -5, -3,
    4, 3, 13, 1, 2, 1, -1, 2,
    3, 5, 8, 4, -5, -6, -8, -11,
    -4, 0, -5, -1, -7, -12, -8, -16,
    -6, -6, 0, 2, -9, -9, -11, -3,
    -9, 2, 3, -1, -5, -13, 4, -20
])

eg_queen_table = np.array([
    -9, 22, 22, 27, 27, 19, 10, 20,
    -17, 20, 32, 41, 58, 25, 30, 0,
    -20, 6, 9, 49, 47, 35, 19, 9,
    3, 22, 24, 45, 57, 40, 57, 36,
    -18, 28, 19, 47, 31, 34, 39, 23,
    -16, -27, 15, 6, 9, 17, 10, 5,
    -22, -23, -30, -16, -16, -23, -36, -32,
    -33, -28, -22, -43, -5, -32, -20, -41
])

eg_king_table = np.array([
    -74, -35, -18, -18, -11, 15, 4, -17,
    -12, 17, 14, 17, 17, 38, 23, 11,
    10, 17, 23, 15, 20, 45, 44, 13,
    -8, 22, 24, 27, 26, 33, 26, 3,
    -18, -4, 21, 24, 27, 23, 9, -11,
    -19, -3, 11, 21, 23, 16, 7, -9,
    -27, -11, 4, 13, 14, 4, -5, -17,
    -53, -34, -21, -11, -28, -14, -24, -43
])

# dictionaries to map pieces to their respective piece-square table

mg_map_dict = {
    chess.PAWN: mg_pawn_table,
    chess.KNIGHT: mg_knight_table,
    chess.BISHOP: mg_bishop_table,
    chess.ROOK: mg_rook_table,
    chess.QUEEN: mg_queen_table,
    chess.KING: mg_king_table
}

eg_map_dict = {
    chess.PAWN: eg_pawn_table,
    chess.KNIGHT: eg_knight_table,
    chess.BISHOP: eg_bishop_table,
    chess.ROOK: eg_rook_table,
    chess.QUEEN: eg_queen_table,
    chess.KING: eg_king_table
}

# -------------- parameters regarding specific evaluations -------------------------------------------------------------
# these parameters are used to weight the different evaluations

BISHOP_PAIR = +50  # bonus for having two bishops
KNIGHT_PAIR = -40  # penalty for having two knights
ROOK_PAIR = -30  # penalty for having two rooks

KNIGHT_PER_PAWN = +6  # bonus for each knight for every pawn
ROOK_PER_PAWN = -6  # penalty for each rook for every pawn
BISHOP_PER_PAWN_ON_COLOUR = -10  # penalty for having a bishop on a square of the same colour as a pawn

MOBILITY = 150  # Material advantage equivalent to having double the amount of moves
SIDE2MOVE_ADV = 40  # Advantage the side to move has over the side which isn't to move (e.g S2M_A = 40 would be +-20)

# -------------- code --------------------------------------------------------------------------------------------------
MATE_VAL = 1000000  # very large number to signify checkmate


def int2mask(integer):
    mask = format(integer, 'b').zfill(64)  # mask represented as bits
    mask = list(map(lambda x: not int(x), mask))  # mask as list of inverted bits [0, 1, 0, etc.]
    return mask


def numOfPiece(board: chess.Board, piece, team=chess.WHITE) -> int:
    if type(piece) == int:
        return len(board.pieces(piece, team))
    elif piece == 'MINORS':
        return numOfPiece(board, chess.KNIGHT, team) + numOfPiece(board, chess.BISHOP, team)


def PawnsOnColour(board: chess.Board, light: bool) -> int:
    # number of pawns on light squares if light = True, else number of pawns on dark squares
    if light:
        pawns = chess.SquareSet(board.pawns) & chess.SquareSet(chess.BB_LIGHT_SQUARES)
    else:
        pawns = chess.SquareSet(board.pawns) & chess.SquareSet(chess.BB_DARK_SQUARES)

    return len(pawns)


def BishopsOnColour(board: chess.Board, light: bool) -> int:
    # number of bishops on light squares if light = True, else number of bishops on dark squares
    if light:
        bishops = chess.SquareSet(board.bishops) & chess.SquareSet(chess.BB_LIGHT_SQUARES)
    else:
        bishops = chess.SquareSet(board.bishops) & chess.SquareSet(chess.BB_DARK_SQUARES)

    return len(bishops)


def isEndgame(board) -> bool:
    middle_game = 2
    for colour in chess.COLORS:
        if numOfPiece(board, chess.QUEEN, team=colour) == 0:  # if this side has no queen
            middle_game -= 1
            continue
        elif numOfPiece(board, 'MINORS', team=colour) <= 1 and numOfPiece(board, chess.ROOK, team=colour) == 0:
            # if this side has no rooks and at most 1 minor piece along with the queen
            middle_game -= 1
            continue
    return not middle_game


def isTactical(board, move):
    return board.is_capture(move) or (move.promotion is not None) or board.gives_check(move) or board.is_check()


def isQuiet(board, move):
    return not isTactical(board, move)


def materialScore(board, team=chess.WHITE):
    if team == chess.BLACK:
        mirror = board.mirror()
        return materialScore(mirror, chess.WHITE)

    # The rest of the calculations occur from the perspective of the white player
    score = 0

    # - 1. naive count of all the material
    for piece in chess.PIECE_TYPES[:-1]:
        score += numOfPiece(board, piece) * piece_value[piece]

    # - 2. benefit bishop pairs and (slightly) punish knight and rook pairs
    score += BISHOP_PAIR * (numOfPiece(board, chess.BISHOP) > 1)
    score += KNIGHT_PAIR * (numOfPiece(board, chess.KNIGHT) > 1)  # KNIGHT_PAIR is negative so += is used
    score += ROOK_PAIR * (numOfPiece(board, chess.ROOK) > 1)  # ditto

    # - 3. benefit knights in a closed position (few pawns), benefit bishops/rooks in open position. average at 10 pawns
    pawns = numOfPiece(board, chess.PAWN, chess.WHITE) + numOfPiece(board, chess.PAWN, chess.BLACK)
    score += KNIGHT_PER_PAWN * (pawns - 10) * numOfPiece(board, chess.KNIGHT)
    score += ROOK_PER_PAWN * (pawns - 10) * numOfPiece(board, chess.ROOK)

    # - 4. benefit bishops which have fewer pawns on their colour
    score += BISHOP_PER_PAWN_ON_COLOUR * BishopsOnColour(board, light=True) * (PawnsOnColour(board, light=True) - 4.5)
    score += BISHOP_PER_PAWN_ON_COLOUR * BishopsOnColour(board, light=False) * (PawnsOnColour(board, light=False) - 4.5)

    # - 5. use piece-square mappings

    boardFlip = board.copy()
    boardFlip.apply_transform(chess.flip_horizontal)  # i have no idea why this step is necessary
    # but the mask is flipped without it for some reason so im just flipping the board

    for piece in chess.PIECE_TYPES:
        piece_mask = boardFlip.pieces(piece, chess.WHITE).mask  # mask as integer
        piece_mask = int2mask(piece_mask)

        if isEndgame(board):
            mx = ma.array(eg_map_dict[piece], mask=piece_mask)
        else:
            mx = ma.array(mg_map_dict[piece], mask=piece_mask)

        piece_score = np.sum(mx) if type(np.sum(mx)) in [np.int32, np.int64] else 0
        score += piece_score

    return score


board_eval_dict = {}


def evaluateBoard(board: chess.Board, team=None) -> float:
    if team is None:
        return evaluateBoard(board, board.turn)
    if team == chess.BLACK:
        mirror = board.mirror()
        return evaluateBoard(mirror, chess.WHITE)

    # The rest of the calculations occur from the perspective of the white player

    # ------------------------------------------ If Game Has Ended --------------------------------------------------- #
    if outcome := board.outcome():
        outcomeDict = {
            chess.WHITE: MATE_VAL,  # White wins
            chess.BLACK: -MATE_VAL,  # Black wins
            None: 0  # Draw
        }
        return outcomeDict[outcome.winner]

    # ------------------------------------------ If Guaranteed Draw -------------------------------------------------- #
    if board.is_insufficient_material():
        return 0

    # ---------------------------------------------------------------------------------------------------------------- #

    boardCopy = board.copy()

    # ------------------Calculate Material Advantage------------------------------------------------------------------ #
    material_advantage = 0
    material_advantage += materialScore(boardCopy, chess.WHITE)
    material_advantage -= materialScore(boardCopy, chess.BLACK)

    # ------------------Calculate Mobility Advantage------------------------------------------------------------------ #
    side2move_advantage = SIDE2MOVE_ADV * (0.5 if (boardCopy.turn == chess.WHITE) else -0.5)

    boardCopy.turn = chess.WHITE
    whiteMoves = boardCopy.pseudo_legal_moves.count()
    boardCopy.turn = chess.BLACK
    blackMoves = boardCopy.pseudo_legal_moves.count()

    mobility_advantage = np.log2(whiteMoves / blackMoves) * MOBILITY
    # ---------------------------------------------------------------------------------------------------------------- #

    del boardCopy
    score = material_advantage + mobility_advantage + side2move_advantage
    return score


if __name__ == "__main__":
    boarder = chess.Board()
