# Flappy Bird Next-Gen — AI Edition

A rebuilt, maintainable Flappy Bird game in Python + Pygame.

## What's improved

- Fixed the original working-directory/path problems by using `pathlib` and paths relative to the project.
- Replaced the old tightly-coupled game loop with a clean `flappy_bird/` package.
- Added a modern menu, pause, restart and game-over screens.
- Added persistent high score in `data/highscore.json`.
- Added adaptive difficulty as the score increases.
- Added **AI Pilot mode**: a deterministic, explainable controller predicts the next pipe gap and automatically flaps.
- Added keyboard controls, sound fallback, FPS-independent movement and safer asset loading.
- Added unit tests for the AI controller and core game calculations.
- Added GitHub Actions CI for syntax checks and tests.
- Keeps the original game assets from the supplied project.

## Requirements

- Python 3.10+
- Pygame 2.6+

## Run locally

### Windows PowerShell

```powershell
cd "D:\path\to\Flappy_bird_Game_Project-main"
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python main.py
```

If PowerShell blocks activation, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### Git Bash

```bash
cd /d/path/to/Flappy_bird_Game_Project-main
python -m venv .venv
source .venv/Scripts/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python main.py
```

## Controls

| Key | Action |
|---|---|
| Space / Up | Flap |
| P | Pause / resume |
| R | Restart after game over |
| A | Toggle AI Pilot |
| M | Toggle sound |
| Esc | Quit |

The mouse can also be clicked/tapped to flap during gameplay.

## AI Pilot

AI Pilot is intentionally local and dependency-free. It is not a cloud API or an LLM. The controller uses the bird's vertical position/velocity and the next pipe's gap to estimate whether a flap is needed. This makes the project reproducible and suitable for a portfolio without API keys.

## Project structure

```text
.
├── main.py
├── requirements.txt
├── requirements-dev.txt
├── flappy_bird/
│   ├── __init__.py
│   ├── ai.py
│   ├── config.py
│   ├── game.py
│   ├── storage.py
│   └── entities/
│       ├── __init__.py
│       ├── bird.py
│       └── pipe.py
├── tests/
│   ├── test_ai.py
│   └── test_entities.py
├── .github/workflows/ci.yml
├── resources/
└── data/
```

## Verify before pushing

```bash
python -m compileall .
pytest -q
python main.py
```

The CI workflow runs compile checks and tests on pushes and pull requests.
