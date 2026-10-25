import pygame
import random
import math
import sys

pygame.init()

# Screen size
WIDTH, HEIGHT = 800, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Zombie Avoidance Game with Power-Ups")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
PLAYER_COLOR = (50, 150, 255)
ZOMBIE_COLOR = (255, 60, 60)
POWER_COLOR = (255, 200, 0)
FREEZE_COLOR = (0, 255, 255)
SHIELD_COLOR = (0, 255, 100)

# Sizes
PLAYER_SIZE = 30
ZOMBIE_SIZE = 30
POWER_SIZE = 20

clock = pygame.time.Clock()

class Player:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.speed = 4
        self.default_speed = 4
        self.shield = False
        self.rect = pygame.Rect(self.x, self.y, PLAYER_SIZE, PLAYER_SIZE)

    def move(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < WIDTH - PLAYER_SIZE:
            self.x += self.speed
        if keys[pygame.K_UP] and self.y > 0:
            self.y -= self.speed
        if keys[pygame.K_DOWN] and self.y < HEIGHT - PLAYER_SIZE:
            self.y += self.speed

        # Keep inside screen
        self.x = max(0, min(self.x, WIDTH - PLAYER_SIZE))
        self.y = max(0, min(self.y, HEIGHT - PLAYER_SIZE))

        self.rect.topleft = (int(self.x), int(self.y))

    def draw(self):
        color = PLAYER_COLOR if not self.shield else SHIELD_COLOR
        pygame.draw.rect(win, color, self.rect)


class Zombie:
    def __init__(self):
        self.x = random.randint(0, WIDTH - ZOMBIE_SIZE)
        self.y = random.randint(0, HEIGHT - ZOMBIE_SIZE)
        self.speed = random.uniform(1.5, 2.5)
        self.rect = pygame.Rect(int(self.x), int(self.y), ZOMBIE_SIZE, ZOMBIE_SIZE)

    def move(self, player):
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)
        if dist != 0:
            dx, dy = dx / dist, dy / dist
            self.x += dx * self.speed
            self.y += dy * self.speed

        self.rect.topleft = (int(self.x), int(self.y))

    def draw(self):
        pygame.draw.rect(win, ZOMBIE_COLOR, self.rect)


class PowerUp:
    def __init__(self):
        self.x = random.randint(20, WIDTH - 40)
        self.y = random.randint(20, HEIGHT - 40)
        self.type = random.choice(["speed", "freeze", "shield"])
        self.rect = pygame.Rect(int(self.x), int(self.y), POWER_SIZE, POWER_SIZE)

    def draw(self):
        if self.type == "speed":
            pygame.draw.rect(win, POWER_COLOR, self.rect)
        elif self.type == "freeze":
            pygame.draw.rect(win, FREEZE_COLOR, self.rect)
        elif self.type == "shield":
            pygame.draw.rect(win, SHIELD_COLOR, self.rect)


def spawn_powerup(powerups):
    # small random chance to spawn a powerup if there are none
    if len(powerups) < 2 and random.randint(1, 300) == 1:
        powerups.append(PowerUp())


score_font = pygame.font.SysFont(None, 32)
big_font = pygame.font.SysFont(None, 48)


def draw_score(score):
    s = score_font.render(f"Score: {int(score)}", True, WHITE)
    win.blit(s, (10, 10))


def show_game_over():
    # Display game over and wait for player's input: R to restart, Q or close to quit
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(160)
    overlay.fill((0, 0, 0))
    win.blit(overlay, (0, 0))

    text = big_font.render("GAME OVER", True, WHITE)
    sub = score_font.render("Press R to Restart or Q to Quit", True, WHITE)
    win.blit(text, ((WIDTH - text.get_width()) // 2, HEIGHT // 2 - 40))
    win.blit(sub, ((WIDTH - sub.get_width()) // 2, HEIGHT // 2 + 10))
    pygame.display.update()

    waiting = True
    while waiting:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_r:
                    return True  # restart
                elif e.key == pygame.K_q:
                    return False  # quit
        clock.tick(10)


def main():
    # Outer loop allows restarting the game without recursion
    while True:
        player = Player()
        zombies = [Zombie()]
        powerups = []
        freeze = False
        freeze_time = 0
        speed_time = 0
        score = 0.0

        running = True
        while running:
            clock.tick(60)
            win.fill(BLACK)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            # Spawn zombies over time (small chance each frame)
            if random.randint(1, 120) == 1:
                zombies.append(Zombie())

            # Spawn power ups
            spawn_powerup(powerups)

            # Move player
            player.move()

            # Move zombies if not frozen
            if not freeze:
                for z in zombies:
                    z.move(player)

            # Check collisions with zombies
            collided_zombie = None
            for z in zombies:
                if player.rect.colliderect(z.rect):
                    collided_zombie = z
                    break

            if collided_zombie:
                if player.shield:
                    player.shield = False
                    try:
                        zombies.remove(collided_zombie)
                    except ValueError:
                        pass
                else:
                    # Game over -> show overlay and wait (returns True to restart)
                    restart = show_game_over()
                    if restart:
                        running = False  # break inner loop; outer while will restart
                        break
                    else:
                        pygame.quit()
                        sys.exit()

            # Collect power-ups
            for p in powerups[:]:
                if player.rect.colliderect(p.rect):
                    if p.type == "speed":
                        player.speed = 7
                        speed_time = pygame.time.get_ticks()
                    elif p.type == "freeze":
                        freeze = True
                        freeze_time = pygame.time.get_ticks()
                    elif p.type == "shield":
                        player.shield = True
                    powerups.remove(p)

            # Timer for speed boost (5 seconds)
            if player.speed > player.default_speed:
                if pygame.time.get_ticks() - speed_time > 5000:
                    player.speed = player.default_speed

            # Timer for freeze (3 seconds)
            if freeze:
                if pygame.time.get_ticks() - freeze_time > 3000:
                    freeze = False

            # Draw everything
            player.draw()
            for z in zombies:
                z.draw()
            for p in powerups:
                p.draw()

            # Score increases over time
            score += 0.05
            draw_score(score)

            pygame.display.update()

        # if we reach here, the player chose restart -> continue outer loop to start fresh
        continue


if __name__ == "__main__":
    main()
