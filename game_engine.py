
"""
GameEngine: owns the puck, both paddles, and the computer AI, and runs
one frame's worth of game logic.

Task 2: Match scoring.
Task 3: 30-second match timer and final result.
Task 4: Reset and relaunch the puck after a goal.
"""

import random
import time
import math

from game.puck import Puck
from game.paddle import Paddle
from game.ai import ComputerAI
from game.collisions import handle_paddle_collision
from game.renderer import WIDTH, HEIGHT, MARGIN, GOAL_TOP, GOAL_BOTTOM

PLAYER_SPEED = 6
PUCK_RADIUS = 12
PADDLE_RADIUS = 28
INITIAL_PUCK_SPEED = 4.5


class GameEngine:
    def __init__(self):
        # Task 2: Initialize scores
        self.player_score = 0
        self.computer_score = 0

        # Task 3: Initialize match timer
        self.match_duration = 30.0
        self.match_start_time = time.monotonic()
        self.remaining_time = self.match_duration
        self.game_over = False
        self.result = None

        self.puck = Puck(WIDTH / 2, HEIGHT / 2, PUCK_RADIUS)
        self._launch_puck()

        self.player = Paddle(
            x=WIDTH * 0.15,
            y=HEIGHT / 2,
            radius=PADDLE_RADIUS,
            min_x=MARGIN + PADDLE_RADIUS,
            max_x=WIDTH / 2 - PADDLE_RADIUS,
            min_y=MARGIN + PADDLE_RADIUS,
            max_y=HEIGHT - MARGIN - PADDLE_RADIUS,
        )

        self.computer = Paddle(
            x=WIDTH * 0.85,
            y=HEIGHT / 2,
            radius=PADDLE_RADIUS,
            min_x=WIDTH / 2 + PADDLE_RADIUS,
            max_x=WIDTH - MARGIN - PADDLE_RADIUS,
            min_y=MARGIN + PADDLE_RADIUS,
            max_y=HEIGHT - MARGIN - PADDLE_RADIUS,
        )

        self.ai = ComputerAI()

    def _launch_puck(self):
        angle_choices = [0.3, 0.6, -0.3, -0.6]
        direction = random.choice([-1, 1])
        vy_factor = random.choice(angle_choices)

        self.puck.vx = INITIAL_PUCK_SPEED * direction
        self.puck.vy = INITIAL_PUCK_SPEED * vy_factor

    def handle_input(self, keys_pressed):
        # Stop player movement after the match ends
        if self.game_over:
            return

        import pygame

        dx = dy = 0

        if keys_pressed[pygame.K_UP]:
            dy -= PLAYER_SPEED
        if keys_pressed[pygame.K_DOWN]:
            dy += PLAYER_SPEED
        if keys_pressed[pygame.K_LEFT]:
            dx -= PLAYER_SPEED
        if keys_pressed[pygame.K_RIGHT]:
            dx += PLAYER_SPEED

        self.player.move_by(dx, dy)

    def update(self):
        # Stop all gameplay after the match ends
        if self.game_over:
            return

        # Task 3: Calculate remaining time using elapsed real time
        elapsed_time = time.monotonic() - self.match_start_time
        self.remaining_time = max(
            0.0,
            self.match_duration - elapsed_time,
        )

        # End match when time reaches zero
        if self.remaining_time <= 0:
            self.game_over = True

            if self.player_score > self.computer_score:
                self.result = "Player Wins"
            elif self.computer_score > self.player_score:
                self.result = "Computer Wins"
            else:
                self.result = "Draw"

            return

        # Existing AI and movement logic
        self.ai.update(self.computer, self.puck)

        self.puck.move()
        self.puck.bounce_off_walls(HEIGHT, MARGIN)

        # Existing collision handling
        handle_paddle_collision(self.puck, self.player)
        handle_paddle_collision(self.puck, self.computer)

        # Check for goals
        self._handle_goals()

    def _handle_goals(self):
        # Left-side goal: player scores
        if self.puck.x - self.puck.radius < MARGIN:
            if GOAL_TOP < self.puck.y < GOAL_BOTTOM:
                self.player_score += 1
                self._reset_puck()
            else:
                self.puck.x = MARGIN + self.puck.radius
                self.puck.vx = -self.puck.vx

        # Right-side goal: computer scores
        elif self.puck.x + self.puck.radius > WIDTH - MARGIN:
            if GOAL_TOP < self.puck.y < GOAL_BOTTOM:
                self.computer_score += 1
                self._reset_puck()
            else:
                self.puck.x = WIDTH - MARGIN - self.puck.radius
                self.puck.vx = -self.puck.vx

    def _reset_puck(self):
        # Task 4: Return puck to the center
        self.puck.x = WIDTH / 2
        self.puck.y = HEIGHT / 2

        # Relaunch the puck so gameplay continues
        self._launch_puck()

    def draw(self, surface, font):
        from game import renderer

        # Draw table and game objects
        renderer.draw_table(surface)

        renderer.draw_paddle(
            surface, self.player, renderer.COLOR_PLAYER
        )
        renderer.draw_paddle(
            surface, self.computer, renderer.COLOR_COMPUTER
        )
        renderer.draw_puck(surface, self.puck)

        # Task 2: Display player score
        player_text = font.render(
            f"Player: {self.player_score}",
            True,
            renderer.COLOR_PLAYER,
        )

        # Task 2: Display computer score
        computer_text = font.render(
            f"Computer: {self.computer_score}",
            True,
            renderer.COLOR_COMPUTER,
        )

        surface.blit(
            player_text,
            (MARGIN + 20, MARGIN + 10),
        )

        surface.blit(
            computer_text,
            (
                WIDTH - MARGIN - computer_text.get_width() - 20,
                MARGIN + 10,
            ),
        )

        # Task 3: Display remaining time
        timer_text = font.render(
            f"Time: {math.ceil(self.remaining_time)}",
            True,
            (255, 255, 255),
        )

        timer_rect = timer_text.get_rect(
            center=(WIDTH // 2, MARGIN + 20)
        )

        surface.blit(timer_text, timer_rect)

        # Task 3: Display final result
        if self.game_over:
            result_text = font.render(
                self.result,
                True,
                (255, 255, 255),
            )

            result_rect = result_text.get_rect(
                center=(WIDTH // 2, HEIGHT // 2)
            )

            surface.blit(result_text, result_rect)
