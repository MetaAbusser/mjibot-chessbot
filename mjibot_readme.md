# mjibot

A chess bot written in Python that plays live games on [Lichess](https://lichess.org) through the Lichess Bot API. It was built as a learning project to explore game-tree search and position evaluation. Board representation and move generation are handled by [python-chess](https://github.com/niklasf/python-chess); the search, evaluation, and time management are my own.

> **Status:** no longer maintained. The code may need updates to work with the current Lichess API.

## Features

### Search
- **Negamax with alpha-beta pruning** (fail-hard)
- **Move ordering** that searches captures first, then checks, then quiet moves, to get more cutoffs
- **Quiescence search** over tactical moves (captures, promotions, and checks) to avoid the horizon effect
- **Mate-distance scoring**, so the bot prefers faster mates and delays being mated

### Time management
- **Iterative deepening** from depth 1 up to depth 5
- Each move uses at most about 5% of the remaining clock. After each iteration, the bot estimates how long the next depth would take from the ratio of the previous two iterations, and stops early if that would exceed the budget.

### Opening book
- Uses a **Polyglot opening book** (`Titans.bin` by default, `Human.bin` included as an alternative) and plays the highest-weighted book move while the position is still in the book.

### Evaluation (`chess_evaluation.py`)
- **Material** with standard piece values (P = 100, N = 300, B = 300, R = 500, Q = 900)
- **PeSTO piece-square tables**, with separate middlegame and endgame tables and a simple endgame detector to switch between them
- **Material imbalance terms**: a bishop-pair bonus, small penalties for knight and rook pairs, and adjustments that favour knights in closed positions and rooks in open ones
- **Bad-bishop penalty** for bishops on the same colour as many pawns
- **Mobility**, scored as the log-ratio of each side's pseudo-legal move count
- A small **side-to-move** bonus

## Project structure

| File | Description |
| --- | --- |
| `chessai.py` | Search, time management, opening book lookup, and the Lichess API loop |
| `chess_evaluation.py` | Static evaluation function and piece-square tables |
| `Titans.bin`, `Human.bin` | Polyglot opening books |

## Requirements

- Python 3.9+
- [`python-chess`](https://pypi.org/project/chess/), `numpy`, `requests`

```bash
pip install chess numpy requests
```

## Usage

1. Create a Lichess account, upgrade it to a BOT account, and generate an API token with the `bot:play` scope.
2. In `chessai.py`, set `key` to your API token and `gameId` to the ID of the game the bot should play.
3. Run:

```bash
python chessai.py
```

By default the bot runs in timed mode (`beBotTimed()`), using iterative deepening and the clock-based time budget. For a fixed-depth search, call `beBot(depth=3)` instead. The bot currently plays as White.

## Acknowledgements

- Piece-square table values from [PeSTO's Evaluation Function](https://www.chessprogramming.org/PeSTO%27s_Evaluation_Function) on the Chess Programming Wiki
- [python-chess](https://github.com/niklasf/python-chess) by Niklas Fiekas for board representation, move generation, and Polyglot book reading
