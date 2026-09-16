from __future__ import annotations

import math
import random
from enum import Enum, auto
from pathlib import Path

import pygame

from .ai import AIPilot, AIObservation
from .config import (
    AUDIO_DIR, BASE_GAP, COLORS, GROUND_Y, HEIGHT, IMAGE_DIR, MIN_GAP,
    PIPE_SPEED, PIPE_WIDTH, ROOT, SPAWN_DISTANCE, WIDTH, FPS
)
from .entities.bird import Bird
from .entities.pipe import PipePair
from .storage import load_high_score, save_high_score

class State(Enum):
    MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()

class AssetLoader:
    def __init__(self):
        self.images = {}
        self.sounds = {}
        self._load_images()
        self._load_sounds()

    def image(self, name: str, fallback_size=None):
        return self.images.get(name)

    def _load_images(self):
        def load(name, path):
            try:
                self.images[name] = pygame.image.load(str(path)).convert_alpha()
            except (FileNotFoundError, pygame.error):
                pass

        for name in ["background-day", "background-night", "base", "gameover", "message"]:
            load(name, IMAGE_DIR / f"{name}.png")
        for color in ["blue", "red", "yellow"]:
            for frame in ["upflap", "midflap", "downflap"]:
                load(f"{color}bird-{frame}", IMAGE_DIR / f"{color}bird-{frame}.png")
        for color in ["green", "red"]:
            load(f"pipe-{color}", IMAGE_DIR / f"pipe-{color}.png")
        for n in range(10):
            load(str(n), IMAGE_DIR / f"{n}.png")

    def _load_sounds(self):
        for name in ["wing", "point", "hit", "die"]:
            path = AUDIO_DIR / f"{name}.wav"
            try:
                self.sounds[name] = pygame.mixer.Sound(str(path))
            except (FileNotFoundError, pygame.error):
                pass

class FlappyBirdGame:
    def __init__(self):
        pygame.init()
        try:
            pygame.mixer.init()
        except pygame.error:
            pass
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Flappy Bird — AI Edition")
        self.clock = pygame.time.Clock()
        self.assets = AssetLoader()
        self.font_big = pygame.font.Font(None, 68)
        self.font = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 26)
        self.state = State.MENU
        self.ai = AIPilot()
        self.ai_enabled = False
        self.sound_enabled = True
        self.high_score = load_high_score()
        self.score = 0
        self.bird = Bird(WIDTH * 0.24, HEIGHT * 0.46)
        self.pipes: list[PipePair] = []
        self.spawn_timer = 0.0
        self.scroll = 0.0
        self.best_run_announced = False
        self.rng = random.Random()

    def run(self):
        running = True
        while running:
            dt = min(self.clock.tick(FPS) / 1000.0, 0.035)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key in (pygame.K_SPACE, pygame.K_UP):
                        if self.state == State.MENU:
                            self.start_game()
                        elif self.state == State.GAME_OVER:
                            self.start_game()
                        elif self.state == State.PLAYING and not self.ai_enabled:
                            self.flap()
                    elif event.key == pygame.K_p and self.state in (State.PLAYING, State.PAUSED):
                        self.state = State.PAUSED if self.state == State.PLAYING else State.PLAYING
                    elif event.key == pygame.K_r and self.state == State.GAME_OVER:
                        self.start_game()
                    elif event.key == pygame.K_a:
                        self.ai_enabled = not self.ai_enabled
                    elif event.key == pygame.K_m:
                        self.sound_enabled = not self.sound_enabled
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.state == State.MENU:
                        self.start_game()
                    elif self.state == State.GAME_OVER:
                        self.start_game()
                    elif self.state == State.PLAYING and not self.ai_enabled:
                        self.flap()

            if self.state == State.PLAYING:
                self.update(dt)
            self.draw()

        pygame.quit()

    def start_game(self):
        self.state = State.PLAYING
        self.score = 0
        self.bird = Bird(WIDTH * 0.24, HEIGHT * 0.46)
        self.pipes = [PipePair.create(WIDTH + 80, self.current_gap(), GROUND_Y)]
        self.spawn_timer = 0.0
        self.best_run_announced = False

    def current_gap(self):
        return max(MIN_GAP, BASE_GAP - self.score * 2.2)

    def current_speed(self):
        return PIPE_SPEED + min(90, self.score * 2.0)

    def flap(self):
        self.bird.flap()
        self.play("wing")

    def play(self, name):
        if self.sound_enabled and name in self.assets.sounds:
            self.assets.sounds[name].play()

    def update(self, dt):
        self.scroll = (self.scroll + self.current_speed() * dt) % 48
        self.bird.update(dt)

        if self.ai_enabled and self.pipes:
            target = min(
                (p for p in self.pipes if p.x + p.width >= self.bird.x),
                key=lambda p: p.x,
                default=None,
            )
            if target:
                obs = AIObservation(
                    self.bird.y, self.bird.velocity, target.gap_top,
                    target.gap_bottom, target.x - self.bird.x
                )
                if self.ai.should_flap(obs):
                    self.flap()

        for pipe in self.pipes:
            pipe.update(dt, self.current_speed())

        self.spawn_timer += dt
        if self.pipes[-1].x < WIDTH - SPAWN_DISTANCE:
            self.pipes.append(PipePair.create(WIDTH + 20, self.current_gap(), GROUND_Y))

        for pipe in self.pipes:
            if not pipe.passed and pipe.x + pipe.width < self.bird.x:
                pipe.passed = True
                self.score += 1
                self.play("point")

        self.pipes = [p for p in self.pipes if p.x + p.width > -20]

        hit = self.bird.hit_bounds(0, GROUND_Y)
        if not hit:
            for pipe in self.pipes:
                if pipe.collides(self.bird.rect, GROUND_Y):
                    hit = True
                    break
        if hit:
            self.game_over()

    def game_over(self):
        self.state = State.GAME_OVER
        self.play("hit")
        self.play("die")
        if self.score > self.high_score:
            self.high_score = self.score
            save_high_score(self.high_score)

    def draw(self):
        self.draw_background()
        if self.state in (State.PLAYING, State.PAUSED, State.GAME_OVER):
            self.draw_pipes()
            self.draw_ground()
            self.draw_bird()
            self.draw_score()
        if self.state == State.MENU:
            self.draw_menu()
        elif self.state == State.PAUSED:
            self.draw_overlay("PAUSED", "Press P to resume")
        elif self.state == State.GAME_OVER:
            self.draw_game_over()
        pygame.display.flip()

    def draw_background(self):
        key = "background-night" if self.ai_enabled else "background-day"
        image = self.assets.image(key)
        if image:
            image = pygame.transform.scale(image, (WIDTH, HEIGHT))
            self.screen.blit(image, (0, 0))
        else:
            self.screen.fill((90, 190, 235))

    def draw_ground(self):
        image = self.assets.image("base")
        if image:
            y = GROUND_Y
            x = -int(self.scroll) % image.get_width()
            while x < WIDTH:
                self.screen.blit(image, (x, y))
                x += image.get_width()
        else:
            pygame.draw.rect(self.screen, (220, 190, 80), (0, GROUND_Y, WIDTH, HEIGHT-GROUND_Y))

    def draw_pipes(self):
        image = self.assets.image("pipe-green")
        for pipe in self.pipes:
            if image:
                top_img = pygame.transform.flip(image, False, True)
                top_scaled = pygame.transform.scale(top_img, (PIPE_WIDTH, max(1, pipe.top_rect.height)))
                bottom_scaled = pygame.transform.scale(image, (PIPE_WIDTH, max(1, GROUND_Y-pipe.bottom_rect.top)))
                self.screen.blit(top_scaled, (pipe.x, 0))
                self.screen.blit(bottom_scaled, (pipe.x, pipe.bottom_rect.top))
            else:
                pygame.draw.rect(self.screen, (60, 190, 70), pipe.top_rect)
                pygame.draw.rect(self.screen, (60, 190, 70), (pipe.x, pipe.bottom_rect.top, PIPE_WIDTH, GROUND_Y-pipe.bottom_rect.top))

    def draw_bird(self):
        color = "blue"
        frame = ["upflap", "midflap", "downflap"][int(pygame.time.get_ticks()/120) % 3]
        image = self.assets.image(f"{color}bird-{frame}")
        if image:
            angle = max(-25, min(90, self.bird.velocity * 0.08))
            rotated = pygame.transform.rotate(image, angle)
            self.screen.blit(rotated, rotated.get_rect(center=(int(self.bird.x), int(self.bird.y))))
        else:
            pygame.draw.circle(self.screen, (255, 235, 60), (int(self.bird.x), int(self.bird.y)), self.bird.radius)

    def draw_score(self):
        text = self.font_big.render(str(self.score), True, COLORS["text"])
        self.screen.blit(text, text.get_rect(center=(WIDTH//2, 70)))

    def draw_menu(self):
        title = self.font_big.render("FLAPPY BIRD", True, COLORS["text"])
        sub = self.font.render("NEXT-GEN • AI EDITION", True, COLORS["accent"])
        prompt = self.font.render("SPACE / CLICK TO START", True, COLORS["text"])
        ai = self.font_small.render(
            f"AI Pilot: {'ON' if self.ai_enabled else 'OFF'}  [A]",
            True, COLORS["text"]
        )
        best = self.font_small.render(f"High Score: {self.high_score}", True, COLORS["text"])
        self.screen.blit(title, title.get_rect(center=(WIDTH//2, 245)))
        self.screen.blit(sub, sub.get_rect(center=(WIDTH//2, 305)))
        self.screen.blit(prompt, prompt.get_rect(center=(WIDTH//2, 405)))
        self.screen.blit(ai, ai.get_rect(center=(WIDTH//2, 455)))
        self.screen.blit(best, best.get_rect(center=(WIDTH//2, 495)))
        hint = self.font_small.render("P: Pause   M: Sound   Esc: Quit", True, COLORS["text"])
        self.screen.blit(hint, hint.get_rect(center=(WIDTH//2, 550)))

    def draw_overlay(self, title, subtitle):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 135))
        self.screen.blit(overlay, (0, 0))
        t = self.font_big.render(title, True, COLORS["text"])
        s = self.font.render(subtitle, True, COLORS["text"])
        self.screen.blit(t, t.get_rect(center=(WIDTH//2, 330)))
        self.screen.blit(s, s.get_rect(center=(WIDTH//2, 395)))

    def draw_game_over(self):
        self.draw_overlay("GAME OVER", f"Score: {self.score}   Best: {self.high_score}")
        s = self.font.render("SPACE / R / CLICK to restart", True, COLORS["accent"])
        self.screen.blit(s, s.get_rect(center=(WIDTH//2, 465)))

if __name__ == "__main__":
    FlappyBirdGame().run()
