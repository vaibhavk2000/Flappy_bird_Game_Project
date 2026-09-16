from flappy_bird.entities.bird import Bird

def test_bird_flap_changes_velocity():
    b = Bird(100, 100)
    b.flap()
    assert b.velocity < 0

def test_bird_moves_down_under_gravity():
    b = Bird(100, 100)
    b.update(0.1)
    assert b.y > 100
