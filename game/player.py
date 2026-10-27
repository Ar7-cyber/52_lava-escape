import pygame

SPEED = 4
GRAVITY = 0.55
MAX_FALL_SPEED = 12
JUMP_VELOCITY = -13
SPRING_VELOCITY = -18

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.vel_y = 0.0
        self.on_ground = True
        self.color = (60, 160, 220)

    def update(self, keys, platforms, width, now):
        dx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += SPEED

        if (keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]) and self.on_ground:
            self.vel_y = JUMP_VELOCITY
            self.on_ground = False

        previous_bottom = self.rect.bottom
        self.vel_y = min(self.vel_y + GRAVITY, MAX_FALL_SPEED)
        self.rect.x = max(0, min(width - self.rect.width, self.rect.x + dx))
        self.rect.y += int(round(self.vel_y))
        self.on_ground = False

        # One-way collision: only land while descending and crossing a platform's top.
        if self.vel_y > 0:
            for platform in platforms:
                if platform.removed:
                    continue
                rect = platform.rect
                horizontal_overlap = self.rect.right > rect.left and self.rect.left < rect.right
                crossed_top = previous_bottom <= rect.top and self.rect.bottom >= rect.top
                if horizontal_overlap and crossed_top:
                    self.rect.bottom = rect.top
                    self.on_ground = True
                    if platform.kind == "spring":
                        self.vel_y = SPRING_VELOCITY
                        self.on_ground = False
                    else:
                        self.vel_y = 0.0
                        platform.landed_on(now)
                    break

    def draw(self, screen, cam_y):
        draw_rect = self.rect.move(0, -int(cam_y))
        pygame.draw.rect(screen, self.color, draw_rect, border_radius=6)
        pygame.draw.circle(
        screen,
        (255, 220, 180),
        (draw_rect.centerx, draw_rect.top + 8),
        7
    )
