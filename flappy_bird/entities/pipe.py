from dataclasses import dataclass
import random
import pygame

@dataclass
class PipePair:
    x: float
    gap_y: float
    gap_size: float
    width: int = 78
    passed: bool = False

    @property
    def top_rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), 0, self.width, int(self.gap_y - self.gap_size / 2))

    @property
    def bottom_rect(self) -> pygame.Rect:
        top = int(self.gap_y + self.gap_size / 2)
        return pygame.Rect(int(self.x), top, self.width, 9999)

    @property
    def gap_top(self) -> float:
        return self.gap_y - self.gap_size / 2

    @property
    def gap_bottom(self) -> float:
        return self.gap_y + self.gap_size / 2

    def update(self, dt: float, speed: float) -> None:
        self.x -= speed * dt

    def collides(self, bird_rect: pygame.Rect, ground_y: int) -> bool:
        return bird_rect.colliderect(self.top_rect) or bird_rect.colliderect(
            pygame.Rect(self.bottom_rect.x, self.bottom_rect.y, self.width, ground_y - self.bottom_rect.y)
        )

    @classmethod
    def create(cls, x: float, gap_size: float, ground_y: int) -> "PipePair":
        margin = 105
        low = margin + gap_size / 2
        high = ground_y - margin - gap_size / 2
        return cls(x=x, gap_y=random.uniform(low, high), gap_size=gap_size)
