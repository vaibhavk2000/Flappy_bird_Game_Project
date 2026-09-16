# Corrections in v2

## Problems found in the supplied project

1. Asset paths used `os.getcwd()`, so launching the game from another directory could break resource loading.
2. `pygame.mixer.init()` could terminate startup on machines without a working audio device.
3. The old loop mixed rendering, input, physics, spawning and scoring in one file.
4. Timing called `clock.tick()` in multiple places, which could make motion inconsistent.
5. The original project depended on several implicit imports from `modules/__init__.py`.
6. The project had no dependency lock/range file, tests or CI.
7. High scores were not persisted.
8. There was no modern AI-assisted gameplay feature.

## v2 solution

The game now has a package structure, relative asset resolution, bounded delta time, safe audio initialization, persistent score storage, deterministic AI Pilot mode, unit tests and GitHub Actions.

The AI Pilot is deliberately simple and transparent rather than pretending to be a trained neural network. It can be upgraded later to a reinforcement-learning agent without changing the game's input/output boundary.
