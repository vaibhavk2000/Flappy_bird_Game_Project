from dataclasses import dataclass
import pygame
from ..config import GRAVITY, FLAP_VELOCITY

@dataclass
class Bird:
    x: float
    y: float
    velocity: float = 0.0
    radius: int = 18

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(
            int(self.x - self.radius),
            int(self.y - self.radius),
            self.radius * 2,
            self.radius * 2,
        )

    def flap(self) -> None:
        self.velocity = FLAP_VELOCITY

    def update(self, dt: float) -> None:
        self.velocity += GRAVITY * dt
        self.y += self.velocity * dt

    def hit_bounds(self, top: float, bottom: float) -> bool:
        return self.y - self.radius <= top or self.y + self.radius >= bottom
