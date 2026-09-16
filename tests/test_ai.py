from flappy_bird.ai import AIPilot, AIObservation

def test_ai_flaps_when_bird_is_below_gap_center():
    ai = AIPilot()
    obs = AIObservation(600, 250, 300, 480, 120)
    assert ai.should_flap(obs)

def test_ai_does_not_always_flap_when_bird_is_centered():
    ai = AIPilot()
    obs = AIObservation(390, -80, 300, 500, 250)
    assert not ai.should_flap(obs)
