import pygame
from game.player import Player
from game.world import generate_platforms, draw_lava

WIDTH, HEIGHT = 500, 640
FPS = 60
BG = (20, 15, 30)
GROUND_Y = HEIGHT + 200
SURGE_PERIOD = 900       # one surge cycle every 15 seconds at 60 FPS
SURGE_DURATION = 180     # surge lasts 3 seconds
BASE_LAVA_SPEED = 0.15

class GameEngine:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Lava Escape")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("monospace", 17, bold=True)
        self.big_font = pygame.font.SysFont("monospace", 42, bold=True)
        self.reset()

    def reset(self):
        self.platforms = generate_platforms(WIDTH, GROUND_Y)
        self.player = Player(WIDTH // 2 - 16, GROUND_Y - 32)
        self.cam_y = 0
        self.lava_y = GROUND_Y + 220
        self.base_lava_rise = BASE_LAVA_SPEED
        self.lava_rise = BASE_LAVA_SPEED
        self.score = 0
        self.game_over = False
        self.won = False
        self.top_y = self.platforms[-1].rect.y
        self.frame = 0
        self.elapsed_seconds = 0.0

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.reset()
        return True

    def update(self):
        if self.game_over or self.won:
            return

        dt = self.clock.get_time() / 1000.0
        self.elapsed_seconds += dt
        now = self.elapsed_seconds
        self.frame += 1

        phase = self.frame % SURGE_PERIOD
        self.surge_active = (
        self.frame >= SURGE_PERIOD
        and phase < SURGE_DURATION
        )
        keys = pygame.key.get_pressed()
        self.player.update(keys, self.platforms, WIDTH, now)

        target = self.player.rect.centery - HEIGHT // 2
        if target < self.cam_y:
            self.cam_y = target

        # The lava accelerates slowly over time; periodic surges add a sharp burst.
        self.base_lava_rise = min(1.2, self.base_lava_rise + 0.0003)
        self.lava_rise = self.base_lava_rise * (2.35 if self.surge_active else 1.0)
        self.lava_y -= self.lava_rise

        for platform in self.platforms:
            platform.update(now)
        self.platforms = [p for p in self.platforms if not p.removed]

        self.score = max(0, (GROUND_Y - self.player.rect.y) // 10)
        if self.player.rect.bottom >= self.lava_y:
            self.game_over = True
        if self.player.rect.top <= self.top_y - 20:
            self.won = True

    def draw(self):
        self.screen.fill(BG)
        now = self.elapsed_seconds
        for platform in self.platforms:
            platform.draw(self.screen, self.cam_y, now)
        self.player.draw(self.screen, self.cam_y)
        draw_lava(self.screen, self.lava_y, self.cam_y, WIDTH, HEIGHT,
                  self.frame, getattr(self, "surge_active", False))

        height_text = self.font.render(
            f"Height: {self.score}m   R: Restart", True, (235, 220, 200))
        self.screen.blit(height_text, (8, 10))

        # Danger meter reflects current lava rise speed relative to the maximum surge speed.
        meter_x, meter_y, meter_w, meter_h = 8, 38, 170, 13
        pygame.draw.rect(self.screen, (65, 55, 65),
                         (meter_x, meter_y, meter_w, meter_h), border_radius=4)
        max_speed = 1.2 * 2.35
        fill_w = int(meter_w * min(1.0, self.lava_rise / max_speed))
        meter_color = (240, 70, 45) if self.surge_active else (245, 175, 50)
        if fill_w > 0:
            pygame.draw.rect(self.screen, meter_color,
                             (meter_x, meter_y, fill_w, meter_h), border_radius=4)
        label = "LAVA SURGE!" if self.surge_active else f"Lava speed: {self.lava_rise:.2f}"
        self.screen.blit(self.font.render(label, True, meter_color),
                         (meter_x + meter_w + 10, meter_y - 3))

        legend = self.font.render("Green: spring   Orange: crumble", True, (210, 205, 220))
        self.screen.blit(legend, (8, HEIGHT - 24))

        if self.game_over:
            self._message("LAVA GOT YOU!", (240, 80, 45))
        elif self.won:
            self._message("ESCAPED!", (80, 230, 120))
        pygame.display.flip()

    def _message(self, text, color):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 165))
        self.screen.blit(overlay, (0, 0))
        title = self.big_font.render(text, True, color)
        subtitle = self.font.render("Press R to Play Again", True, (220, 220, 220))
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 40))
        self.screen.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, HEIGHT // 2 + 20))

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()
