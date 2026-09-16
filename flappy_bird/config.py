from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = ROOT / "resources"
IMAGE_DIR = ASSET_DIR / "images"
AUDIO_DIR = ASSET_DIR / "audios"
DATA_DIR = ROOT / "data"

WIDTH = 432
HEIGHT = 768
FPS = 60

GROUND_RATIO = 0.82
GROUND_Y = int(HEIGHT * GROUND_RATIO)

GRAVITY = 1500.0
FLAP_VELOCITY = -430.0
PIPE_SPEED = 190.0
PIPE_WIDTH = 78
BASE_GAP = 185
MIN_GAP = 135
SPAWN_DISTANCE = 310

COLORS = {
    "text": (255, 255, 255),
    "shadow": (20, 20, 30),
    "panel": (20, 28, 40),
    "accent": (255, 214, 70),
    "danger": (245, 90, 90),
}
