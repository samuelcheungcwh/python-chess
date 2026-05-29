from pathlib import Path

# Project root (2 levels above this file if inside src/)
ROOT_DIR = Path(__file__).resolve().parent.parent.parent

# Engine settings
ENGINE_PATH = ROOT_DIR / "stockfish/stockfish-macos-m1-apple-silicon"

ENGINE_CONFIG = {
    "Threads": 1,
    "Hash": 64,
}

DEFAULT_DEPTH = 15