import json
from pathlib import Path
from .config import DATA_DIR

HIGH_SCORE_FILE = DATA_DIR / "highscore.json"

def load_high_score() -> int:
    try:
        data = json.loads(HIGH_SCORE_FILE.read_text(encoding="utf-8"))
        return max(0, int(data.get("high_score", 0)))
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return 0

def save_high_score(score: int) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    HIGH_SCORE_FILE.write_text(
        json.dumps({"high_score": int(max(0, score))}, indent=2),
        encoding="utf-8",
    )
