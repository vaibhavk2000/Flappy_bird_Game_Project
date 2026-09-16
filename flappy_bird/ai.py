from dataclasses import dataclass

@dataclass(frozen=True)
class AIObservation:
    bird_y: float
    bird_velocity: float
    gap_top: float
    gap_bottom: float
    pipe_x: float

class AIPilot:
    """Small deterministic controller; no network/API/model dependency."""

    def should_flap(self, obs: AIObservation) -> bool:
        gap_center = (obs.gap_top + obs.gap_bottom) / 2
        # Look ahead more when moving downward and reduce the target slightly
        # so the bird does not continuously chase the top of the gap.
        target = gap_center - min(max(obs.bird_velocity, 0) * 0.045, 28)
        distance = obs.pipe_x
        urgency = max(0.0, 1.0 - distance / 360.0)
        return obs.bird_y > target + 18 + urgency * 12 or (
            obs.bird_velocity > 330 and obs.bird_y > target
        )
