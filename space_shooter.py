import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Game Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GRAY = (150, 150, 150)
CYAN = (0, 255, 255)

# --- Sound & Music ---
pygame.mixer.init()

laser_sound = pygame.mixer.Sound("pew.mp3")
laser_sound.set_volume(0.3)

explosion_sound = pygame.mixer.Sound("Wilhelm Scream - Sound Effect (HD).mp3")
explosion_sound.set_volume(0.5)

MENU_MUSIC = "music_track1.mp3"
GAME_MUSIC = "music_track2.mp3"
pygame.mixer.music.load(MENU_MUSIC)
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1)

# Setup Game Window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
background = pygame.image.load("space-odyssey.jpg").convert()
background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
background2 = pygame.image.load("download_2.webp").convert()
background2 = pygame.transform.scale(background2, (SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Emily and Ariana's space shooter")
clock = pygame.time.Clock()

enemy_images = [
    pygame.image.load("scrat.webp"),
    pygame.image.load("images.jpeg")
]

# Global Difficulty Settings (min_speed, max_speed)
difficulty_speeds = {
    "Easy": (2, 5),
    "Medium": (5, 9),
    "IMPOSSIBLE": (22, 30)
}
current_difficulty = "Medium"  # Default fallback

def draw_hearts(surf, x, y, player_lives):
    # Colors for the health indicators
    HEART_RED = (255, 0, 50)
    LAVA = (80, 85, 88) # Visible silhouette on black background


    for i in range(3):
        # Determine coordinate shifting for each heart slot (spaced 35 pixels apart)
        heart_x = x - (i * 35)

        color = HEART_RED if (3 - i) <= player_lives else LAVA


        pygame.draw.polygon(surf, color, [
            (heart_x, y + 8), 
            (heart_x - 12, y - 6), 
            (heart_x - 6, y - 12), 
            (heart_x, y - 5), 
            (heart_x + 6, y - 12), 
            (heart_x + 12, y - 6)
        ])

# --- Classes ---

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((54, 50), pygame.SRCALPHA)
        DARK_GREEN = (0, 150, 0)
        CYAN_COCKPIT = (0, 255, 255)
        ORANGE_THRUSTER = (255, 100, 0)
        pygame.draw.polygon(self.image, ORANGE_THRUSTER, [(27, 50), (22, 42), (32, 42)])
        pygame.draw.polygon(self.image, WHITE, [(27, 0), (16, 35), (38, 35)])

        pygame.draw.polygon(self.image, GREEN, [(16, 25), (0, 42), (16, 38)])       # Left wing
        pygame.draw.polygon(self.image, GREEN, [(38, 25), (54, 42), (38, 38)])      # Right wing
        pygame.draw.polygon(self.image, DARK_GREEN, [(16, 38), (27, 42), (38, 38)]) # Wing base

        pygame.draw.polygon(self.image, CYAN_COCKPIT, [(27, 10), (22, 25), (32, 25)])

        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 20
        self.speed = 6

        self.weapon_level = 1  # 1 = single straight shot, 2 = 3-way spray
        self.weapon_expire = 0
        self.shield = False    # True = absorbs one enemy hit
        self.health = 3

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

        if self.weapon_level > 1 and pygame.time.get_ticks() > self.weapon_expire:
            self.weapon_level = 1

    def upgrade_weapon(self):
        self.weapon_level = min(3, self.weapon_level + 1)
        self.weapon_expire = pygame.time.get_ticks() + 3000

    def shoot(self):
        if self.weapon_level == 1:
            angles = [0]                    # one vertical laser
        elif self.weapon_level == 2:
            angles = [-4, 0, 4]             # 3-way spray
        else:
            angles = [-6, -3, 0, 3, 6]      # 5-way spray

        for angle_speed in angles:
            bullet = Bullet(self.rect.centerx, self.rect.top, speedx=angle_speed)
            all_sprites.add(bullet)
            bullets.add(bullet)

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.width = 50
        self.height = 50
        random_png = random.choice(enemy_images)
        self.image = pygame.transform.scale(random_png, (self.width, self.height)).convert_alpha()

        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randint(-100, -40)

        # enemy health (i.e. amount of hits to take before death)
        self.health = 3

        # Speed dynamic scaling based on selected difficulty
        min_s, max_s = difficulty_speeds[current_difficulty]
        self.speedy = random.randint(min_s, max_s)

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > SCREEN_HEIGHT:
            self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
            self.rect.y = random.randint(-100, -40)
            self.health = 3  # come back at full health
            min_s, max_s = difficulty_speeds[current_difficulty]
            self.speedy = random.randint(min_s, max_s)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speedx=0):
        super().__init__()
        self.image = pygame.Surface((6, 15))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = -10
        self.speedx = speedx

    def update(self):
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        if (self.rect.bottom < 0 or self.rect.right < 0 or self.rect.left > SCREEN_WIDTH):
            self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Square canvas for the explosion circle
        self.image = pygame.Surface((60, 60), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

        self.radius = 5           # Starting size of the explosion
        self.max_radius = 30      # Maximum size before it fades
        self.growth_speed = 3     # How fast it expands per frame

    def update(self):
        self.radius += self.growth_speed
        self.image.fill((0, 0, 0, 0))  # Clear transparent background
        alpha = max(0, 255 - int((self.radius / self.max_radius) * 255))

        pygame.draw.circle(self.image, (255, 100, 0, alpha), (30, 30), self.radius)
        pygame.draw.circle(self.image, (255, 255, 0, alpha), (30, 30), max(1, self.radius - 6))

        if self.radius >= self.max_radius:
            self.kill()

class Upgrade(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Upgrade type chosen randomly: "shield" or "weapon"
        self.type = random.choice(["shield", "weapon"])

        self.image = pygame.Surface((25, 25))
        if self.type == "shield":
            self.image.fill(CYAN)    # Cyan box = shield
        else:
            self.image.fill(YELLOW)  # Yellow box = weapon upgrade

        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.speedy = 3  # Slowly drifts downward

    def update(self):
        self.rect.y += self.speedy
        # Delete if it falls past the screen
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


# --- UI Helpers ---
font_name = pygame.font.match_font('arial')
def draw_text(surf, text, size, x, y, color=WHITE):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)

def draw_menu():
    screen.blit(background, (0, 0))
    draw_text(screen, "SPACE SHOOTER", 60, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4, YELLOW)
    draw_text(screen, "Select Difficulty Level:", 30, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40, WHITE)

    draw_text(screen, "Press [1] for EASY", 24, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10, GREEN)
    draw_text(screen, "Press [2] for MEDIUM", 24, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 45, WHITE)
    draw_text(screen, "Press [3] for IMPOSSIBLE", 24, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80, RED)

    draw_text(screen, "Controls: Move with A/D or Arrow keys. Left-Click Mouse to Shoot.", 16, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50, GRAY)
    pygame.display.flip()

# --- Initialize Game Objects Engine Helper ---
def start_new_game():
    global all_sprites, enemies, bullets, upgrades, player, score, game_over, lives
    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    upgrades = pygame.sprite.Group()

    player = Player()
    all_sprites.add(player)

    for i in range(8):
        enemy = Enemy()
        all_sprites.add(enemy)
        enemies.add(enemy)

    score = 0
    lives = 3
    game_over = False

# Game Engine State Tracking Variables
show_menu = True
running = True

# --- Core Game Loop ---
while running:
    clock.tick(FPS)

    # State 1: Displaying the Main Difficulty Menu
    if show_menu:
        draw_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_1, pygame.K_2, pygame.K_3]:
                    if event.key == pygame.K_1:
                        current_difficulty = "Easy"
                    elif event.key == pygame.K_2:
                        current_difficulty = "Medium"
                    elif event.key == pygame.K_3:
                        current_difficulty = "IMPOSSIBLE"

                    pygame.mixer.music.stop()
                    pygame.mixer.music.load(GAME_MUSIC)
                    pygame.mixer.music.set_volume(0.3)
                    pygame.mixer.music.play(-1)

                    show_menu = False
                    start_new_game()
        continue  # Bypass the main gameplay step while in menu mode

    # State 2: Active Gameplay Loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and not game_over:
                player.shoot()
                laser_sound.play()

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and game_over:
                pygame.mixer.music.stop()
                pygame.mixer.music.load(MENU_MUSIC)
                pygame.mixer.music.play(-1)
                show_menu = True  # Loop back into selection menu on restart

    if not game_over:
        all_sprites.update()

        # Check Laser vs Enemy Collisions
        hits = pygame.sprite.groupcollide(enemies, bullets, False, True)

        for enemy in hits:
            enemy.health -= 1

            if enemy.health <= 0:
                score += 10

                # 30% chance to drop an upgrade
                if random.random() < 0.30:
                    item = Upgrade(enemy.rect.centerx, enemy.rect.centery)
                    all_sprites.add(item)
                    upgrades.add(item)

                explosion_sound.play()
                expl = Explosion(enemy.rect.centerx, enemy.rect.centery)
                all_sprites.add(expl)
                enemy.kill()

                new_enemy = Enemy()
                all_sprites.add(new_enemy)
                enemies.add(new_enemy)

        # Player picks up upgrades
        for item in pygame.sprite.spritecollide(player, upgrades, True):
            if item.type == "weapon":
                player.upgrade_weapon()
            elif item.type == "shield":
                player.shield = True

        # Check Enemy vs Player Collisions
        # True = the enemy that touched you is removed, so a shield only gets used once
        player_hit = pygame.sprite.spritecollide(player, enemies, True)
        if player_hit:
            if player.shield:
                player.shield = False
                for e in player_hit:
                    explosion_sound.play()
                    all_sprites.add(Explosion(e.rect.centerx, e.rect.centery))
                    new_enemy = Enemy()
                    all_sprites.add(new_enemy)
                    enemies.add(new_enemy)
            else:
                lives -= 1

                enemy = Enemy()
                all_sprites.add(enemy)
                enemies.add(enemy)

                if lives <= 0:
                    game_over = True

    # Render Graphics Layer
    screen.blit(background2, (0, 0))
    all_sprites.draw(screen)

    # Shield bubble around the ship
    if player.shield:
        pygame.draw.circle(screen, CYAN, player.rect.center, 40, 2)

    draw_text(screen, f"SCORE: {score}", 24, SCREEN_WIDTH // 2, 10)
    draw_text(screen, f"MODE: {current_difficulty}", 16, 60, 15, GRAY)

    draw_hearts(screen, 760, 20, lives)

    if game_over:
        draw_text(screen, "GAME OVER", 50, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50, RED)
        draw_text(screen, "Press [R] to Return to Menu", 22, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10, WHITE)

    pygame.display.flip()

pygame.quit()
sys.exit()
