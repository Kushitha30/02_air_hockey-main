"""
collisions: puck-vs-paddle collision handling.
"""

import math


def handle_paddle_collision(puck, paddle):
    """
    If the puck overlaps the paddle, bounce it off.
    Returns True if a collision was handled this frame.
    """
    dx = puck.x - paddle.x
    dy = puck.y - paddle.y
    distance = math.sqrt(dx * dx + dy * dy)

    min_distance = puck.radius + paddle.radius

    if distance < min_distance:

        # Avoid division by zero
        if distance == 0:
            nx, ny = 1.0, 0.0
        else:
            # Collision normal: paddle -> puck
            nx = dx / distance
            ny = dy / distance

        # Check whether the puck is moving toward the paddle
        velocity_toward_paddle = puck.vx * nx + puck.vy * ny

        if velocity_toward_paddle < 0:
            # Reflect velocity around the collision normal
            dot = puck.vx * nx + puck.vy * ny

            puck.vx = puck.vx - 2 * dot * nx
            puck.vy = puck.vy - 2 * dot * ny

        # Push puck outside the paddle
        overlap = min_distance - distance

        puck.x += nx * overlap
        puck.y += ny * overlap

        return True

    return False