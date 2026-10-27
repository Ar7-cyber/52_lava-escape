import math
import random
import pygame

PLATFORM_COLOR = (100, 80, 50)
CRUMBLE_COLOR = (207, 112, 54)
SPRING_COLOR = (70, 210, 130)
LAVA_COLOR = (230, 65, 25)


class Platform:
    """A one-way platform with optional crumbling or spring behavior."""

    def __init__(self, x, y, width, height=16, kind="normal"):
        self.rect = pygame.Rect(x, y, width, height)
        self.kind = kind
        self.crumble_started_at = None
        self.crumble_duration = 0.9
        self.removed = False

    def landed_on(self, now):
        if self.kind == "crumble" and self.crumble_started_at is None:
            self.crumble_started_at = now

    def update(self, now):
        if (
            self.kind == "crumble"
            and self.crumble_started_at is not None
            and now - self.crumble_started_at >= self.crumble_duration
        ):
            self.removed = True

    def draw(self, screen, cam_y, now):
        if self.removed:
            return

        rect = self.rect.move(0, -int(cam_y))
        color = PLATFORM_COLOR

        if self.kind == "crumble":
            color = CRUMBLE_COLOR

            if self.crumble_started_at is not None:
                elapsed = now - self.crumble_started_at
                shake = int(
                    math.sin(now * 55) * min(4, 1 + elapsed * 5)
                )
                rect.x += shake

        elif self.kind == "spring":
            color = SPRING_COLOR

        pygame.draw.rect(screen, color, rect, border_radius=4)

        if self.kind == "spring":
            pygame.draw.line(
                screen,
                (225, 255, 235),
                (rect.left + 5, rect.centery),
                (rect.right - 5, rect.centery),
                3,
            )


def generate_platforms(width, base_y, count=30):
    """
    Generate a climbable route.

    Consecutive platforms have controlled vertical and horizontal gaps.
    Spring and crumbling platforms are optional variations, not the only
    route forward.
    """
    ground = Platform(0, base_y, width, 20, "normal")
    platforms = [ground]

    previous_x = width // 2 - 70
    previous_width = 140
    y = base_y

    for i in range(count):
        # A normal jump can comfortably cover these vertical gaps.
        vertical_gap = random.randint(65, 82)
        y -= vertical_gap

        platform_width = random.randint(115, 165)

        # Keep the next platform reasonably close horizontally.
        max_horizontal_gap = 85
        min_x = max(
            0,
            previous_x - max_horizontal_gap - platform_width + 1
        )
        max_x = min(
            width - platform_width,
            previous_x + previous_width + max_horizontal_gap - 1
        )

        if min_x > max_x:
            x = max(0, min(width - platform_width, previous_x))
        else:
            x = random.randint(min_x, max_x)

        # Keep most platforms normal, so progress never depends on a
        # spring or on landing on a platform that will soon disappear.
        roll = random.random()

        if roll < 0.12:
            kind = "spring"
        elif roll < 0.27:
            kind = "crumble"
        else:
            kind = "normal"

        platforms.append(
            Platform(x, y, platform_width, 16, kind)
        )

        previous_x = x
        previous_width = platform_width

    return platforms


def draw_lava(screen, lava_y, cam_y, width, height, frame, surge=False):
    ly = int(lava_y - cam_y)

    if ly < height:
        points = [(0, ly)]

        for x in range(0, width + 20, 20):
            wave = int(
                math.sin(
                    x * 0.08 + frame * (0.16 if surge else 0.1)
                ) * (10 if surge else 8)
            )
            points.append((x, ly + wave))

        points.extend([(width, height), (0, height)])
        pygame.draw.polygon(screen, LAVA_COLOR, points)

        glow = pygame.Surface((width, 30), pygame.SRCALPHA)

        for i in range(15):
            alpha = max(0, 70 - i * 4)
            pygame.draw.line(
                glow,
                (255, 100, 0, alpha),
                (0, i),
                (width, i),
                1,
            )

        screen.blit(glow, (0, ly - 15))