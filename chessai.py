import chess
import chess.polyglot
from chess_evaluation import evaluateBoard, isTactical, MATE_VAL  # my own library
import numpy as np
import requests
import json
import time
# import ai_lib as ai


def streamMovesStack():
    s = requests.Session()
    r = s.get(f'https://lichess.org/api/bot/game/stream/{gameId}', headers=headers, stream=True)
    for line in r.iter_lines():
        if not line:
            continue

        d_line = line.decode('utf-8')
        d = json.loads(d_line)

        if "state" in d:
            d = d["state"]

        if "moves" in d:
            moves = d["moves"].split()
            timeLeft = d["wtime"] / 1000
            print(d)
            print(f'{moves= }, {timeLeft= }')
            yield moves, timeLeft


def playMove(move_san):
    return requests.post(f'https://lichess.org/api/bot/game/{gameId}/move/{move_san}', headers=headers)


########################################################################################################################

def evaluateMove(board, move, check_priority: bool = False):
    board.push(move)
    value = evaluateBoard(board, chess.WHITE)
    board.pop()
    if check_priority:
        value += 500 * board.gives_check(move)
        value += 500 * board.is_capture(move)
    return value


def sortLegalMoves(board: chess.Board):
    def prioritise(move):
        if board.is_capture(move):
            return 0
        elif board.gives_check(move):
            return 1
        else:
            return 2

    moveList = sorted(board.legal_moves, key=prioritise)
    return moveList
    # return sorted(board.legal_moves, key=lambda x: evaluateMove(board, move=x, check_priority=True), reverse=reverse)


def generateTacticalMoves(board):
    for move in board.legal_moves:
        if isTactical(board, move):
            yield move


########################################################################################################################
def negamaxRoot(board: chess.Board, depth: int, alpha=-np.inf, beta=np.inf) -> tuple[chess.Move, float]:
    totalMoves = board.legal_moves.count()
    i = 0

    bestMove = chess.Move(0, 0)
    for move in sortLegalMoves(board):
        i += 1
        print(f'{(100 * i / totalMoves):.0f}%')  # shows progress

        board.push(move)
        score = -negamax(board, depth - 1, -beta, -alpha)
        board.pop()

        if score >= beta:
            print('beta cutoff weird')
            return move, beta
        if score > alpha:
            alpha = score
            bestMove = move

    return bestMove, alpha


def quiesce(board: chess.Board, depth: int = -1, alpha=-np.inf, beta=np.inf) -> float:

    stand_pat = evaluateBoard(board)
    if depth == 0 or board.is_game_over():  # terminal node
        return stand_pat

    if stand_pat >= beta:
        return beta
    if stand_pat > alpha:
        alpha = stand_pat
    # ------------------------------------------------------------------------------------------------------------------
    for move in generateTacticalMoves(board):

        board.push(move)
        score = -quiesce(board, depth - 1, -beta, -alpha)
        board.pop()

        if score >= beta:
            return beta  # fail hard beta-cutoff
        if score > alpha:
            alpha = score  # alpha acts like max in MiniMax

    return alpha


def negamax(board: chess.Board, depth: int, alpha=-np.inf, beta=np.inf) -> float:
    if board.is_game_over():
        score = quiesce(board, -1, alpha, beta)
        if score == MATE_VAL:  # if white is mating, prioritise smaller depth to mate
            score += depth  # i.e. reward each point of depth remaining
        elif score == -MATE_VAL:  # if black is mating, prioritise longer depth to mate
            score -= depth  # i.e. penalise each point of depth remaining

        return score

    if depth == 0:  # terminal node
        score = quiesce(board, 10, alpha, beta)
        return score

    # ------------------------------------------------------------------------------------------------------------------
    for move in sortLegalMoves(board):

        board.push(move)
        score = -negamax(board, depth - 1, -beta, -alpha)
        board.pop()

        if score >= beta:
            return beta  # fail hard beta-cutoff
        if score > alpha:
            alpha = score  # alpha acts like max in MiniMax

    return alpha


########################################################################################################################

def bookMoveQuery(board):
    with chess.polyglot.open_reader(openingBook) as reader:
        moves = list(sorted(reader.find_all(board), key=lambda x: x.weight, reverse=True))

    return moves[0].move


def findBestMove(board, depth):
    try:  # if in opening book
        next_move, evaluation = bookMoveQuery(board), 0  # do move from opening book
        book = True
        print('Book Move')
    except IndexError:
        next_move, evaluation = negamaxRoot(board, depth)
        book = False

    return next_move, evaluation, book


def beBot(depth):
    Chess_board = chess.Board()

    botTurn = chess.WHITE
    moveStackCur = ['im a dummy']
    for moveStack, _ in streamMovesStack():
        if moveStackCur == moveStack:
            continue
        moveStackCur = moveStack

        Chess_board.reset()
        for move in moveStack:
            Chess_board.push_san(move)

        if Chess_board.turn is not botTurn:
            print('not bot turn')
            continue
        # --------------------------------------------------------------------------------------------------------------

        print('thinking...')
        st = time.time()
        # ---
        next_move, evaluation, _ = findBestMove(Chess_board, depth)
        # ---
        et = time.time()
        playMove(next_move)

        Chess_board.push(next_move)
        print(Chess_board)
        evaluation /= 100
        print(f'{evaluation = :.2f}')
        print(f'computation time: {et - st :.2f}s')


# noinspection PyUnboundLocalVariable
def beBotTimed():
    Chess_board = chess.Board()

    botTurn = chess.WHITE
    moveStackCur = ['im a dummy']
    for moveStack, timeLeft in streamMovesStack():
        if moveStackCur == moveStack:
            continue
        moveStackCur = moveStack

        Chess_board.reset()
        for move in moveStack:
            Chess_board.push_san(move)

        if Chess_board.turn is not botTurn:
            print('not bot turn')
            continue
        # --------------------------------------------------------------------------------------------------------------
        print('thinking...')

        timeUpper = timeLeft * 0.05  # 5% of time to be used up (max) for this move

        startTime = time.time()
        for depth in range(1, 6):

            next_move, evaluation, book = findBestMove(Chess_board, depth)
            timeTaken = time.time() - startTime
            if book:
                break

            if depth == 1:
                t1 = timeTaken
                timeLower = timeUpper * 1/8  # time taken to make a move should be at least 1/8 of timeUpper as t ~ 8^d
                # exact exponential varies with depth and board state, but this is a good approximation until we sample
            else:
                t2 = timeTaken
                timeLower = timeUpper * t1/t2  # update timeLower based on previous and current times
                t1 = t2

            if timeTaken > timeLower:  # if time taken is greater than timeLower, stop searching to avoid time loss
                break

        # --------------------------------------------------------------------------------------------------------------

        playMove(next_move)
        Chess_board.push(next_move)
        print(Chess_board)
        evaluation /= 100
        print(f'{evaluation = :.2f}')
        print(f'computation time: {timeTaken :.2f}s')


key = "lip_BJZAZkE7i3qIhkVWu9C7"  # my bot's lichess API key ( top secret 0.0 )
headers = {'Authorization': f'Bearer {key}'}
gameId = "iu9A6pD5"
openingBook = "Titans.bin"

if __name__ == "__main__":
    # beBot(depth=3)
    beBotTimed()




