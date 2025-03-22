import pgzrun
import random

WIDTH = 800
HEIGHT = 600
GROUND_Y = 550
MAX_BOUNCES = 5
BASE_BULLET_DAMAGE = 25
BASE_SHOOT_COOLDOWN = 30

run_frames = ["run_frames/run1", "run_frames/run2", "run_frames/run4", "run_frames/run5"]
shoot_frames = ["shoot_effects/1", "shoot_effects/2", "shoot_effects/3", 
                "shoot_effects/4", "shoot_effects/5", "shoot_effects/6"]
idle_frames = ["idle/idle1", "idle/idle2", "idle/idle3", "idle/idle4", "idle/idle5", "idle/idle6"]

game_state = "menu"
score = 0
game_over = False
sound_enabled = True

start_button = Rect((300, 200), (200, 50))
sound_button = Rect((300, 280), (200, 50))
quit_button = Rect((300, 360), (200, 50))

resume_button = Rect((300, 200), (200, 50))
pause_sound_button = Rect((300, 280), (200, 50))
pause_quit_button = Rect((300, 360), (200, 50))

level_bar_border = Rect((100, 10), (200, 20))
level_bar = Rect((102, 12), (0, 16))

frame_index = 0
shoot_index = 0
shooting = False
shoot_timer = 0
shoot_cooldown = 0

gun = Actor("gun")
gun.visible = True

shoot_effect = Actor(shoot_frames[0])
shoot_effect.visible = False

bullets = []
enemies = []
enemy_spawn_timer = 0

class Enemy(Actor):
    def __init__(self, image, position):
        super().__init__(image, position)
        self.health = random.randint(1, 100)
        self.bounce_count = 0
        self.initial_height = GROUND_Y
        self.speed = random.uniform(1, 3)
        self.initial_speed = self.speed
        self.is_prize = False
    
    def take_damage(self, amount):
        self.health -= amount
        return self.health <= 0
    
    def update(self):
        self.y += self.speed
        if self.y >= GROUND_Y - 20 and self.speed > 0:
            self.bounce_count += 1
            self.initial_height *= 0.5
            self.speed *= -1
            self.image = "asteroid_angry"
        elif (self.y <= self.initial_height) and (self.speed < 0):
            self.speed *= -1
        return self.bounce_count >= MAX_BOUNCES

class Player(Actor):
    def __init__(self, image, position):
        super().__init__(image, position)
        self.direction = "right"
        self.state = "idle"
        self.level = 1
        self.max_health = 100
        self.health = self.max_health
        self.xp = 0
        self.xp_needed = 4
    
    def gain_xp(self, amount):
        self.xp += amount
        
        if self.xp >= self.xp_needed:
            self.level_up()
    
    def level_up(self):
        self.level += 1
        self.xp = 0
        self.xp_needed = 4 ** self.level
        
        self.max_health = 100 + (self.level - 1) * 50
        self.health = self.max_health

player = Player(run_frames[0], (400, GROUND_Y - 25))

def draw():
    screen.clear()
    
    if game_state == "menu":
        draw_menu()
    elif game_state == "playing":
        draw_game()
    elif game_state == "paused":
        draw_game()
        draw_pause_menu()

def draw_menu():
    screen.fill((50, 50, 100))
    
    screen.draw.text("SHOOTER GAME", center=(400, 100), fontsize=60, color="white")
    
    screen.draw.filled_rect(start_button, (100, 100, 200))
    screen.draw.rect(start_button, "white")
    screen.draw.text("START", center=start_button.center, fontsize=30, color="white")
    
    screen.draw.filled_rect(sound_button, (100, 100, 200))
    screen.draw.rect(sound_button, "white")
    sound_text = "SOUND: ON" if sound_enabled else "SOUND: OFF"
    screen.draw.text(sound_text, center=sound_button.center, fontsize=30, color="white")
    
    screen.draw.filled_rect(quit_button, (100, 100, 200))
    screen.draw.rect(quit_button, "white")
    screen.draw.text("QUIT", center=quit_button.center, fontsize=30, color="white")

def draw_pause_menu():
    overlay = Rect((0, 0), (WIDTH, HEIGHT))
    screen.draw.filled_rect(overlay, (0, 0, 0, 128))
    
    screen.draw.text("PAUSED", center=(400, 100), fontsize=60, color="white")
    
    screen.draw.filled_rect(resume_button, (100, 100, 200))
    screen.draw.rect(resume_button, "white")
    screen.draw.text("RESUME", center=resume_button.center, fontsize=30, color="white")
    
    screen.draw.filled_rect(pause_sound_button, (100, 100, 200))
    screen.draw.rect(pause_sound_button, "white")
    sound_text = "SOUND: ON" if sound_enabled else "SOUND: OFF"
    screen.draw.text(sound_text, center=pause_sound_button.center, fontsize=30, color="white")
    
    screen.draw.filled_rect(pause_quit_button, (100, 100, 200))
    screen.draw.rect(pause_quit_button, "white")
    screen.draw.text("QUIT", center=pause_quit_button.center, fontsize=30, color="white")

def draw_game():
    screen.fill((128, 128, 255))
    
    screen.draw.text(f"Score: {score}", (10, 10), fontsize=30, color="white")
    
    draw_level_bar()

    if game_over:
        screen.draw.text("GAME OVER", center=(400, 300), fontsize=60, color="red")
        screen.draw.text("Press ESC to return to menu", center=(400, 350), fontsize=30, color="white")
        if sound_enabled:
            sounds.game_over.play(1)
    
    player.draw()
    gun.draw()
    shoot_effect.draw()

    for bullet in bullets:
        bullet.draw()
        
    for enemy in enemies:
        enemy.draw()
        screen.draw.text(f"{enemy.health}", center=(enemy.x, enemy.y), fontsize=20, color="white", 
                        shadow=(1, 1), scolor="black")

    screen.draw.filled_rect(Rect((0, GROUND_Y), (WIDTH, HEIGHT - GROUND_Y)), (0, 255, 0))

def draw_level_bar():
    screen.draw.text(f"Level: {player.level}", (140, 35), fontsize=20, color="white")
    
    if player.xp_needed > 0:
        progress = player.xp / player.xp_needed
    else:
        progress = 1

    level_bar.width = int(196 * progress)
    screen.draw.filled_rect(level_bar_border, (100, 100, 100))
    screen.draw.filled_rect(level_bar, (0, 255, 0))
    screen.draw.rect(level_bar_border, "white")

def update():
    global game_over, game_state
    
    if game_state == "menu":
        pass
    elif game_state == "playing":
        if not game_over:
            update_game()

def update_game():
    global frame_index, shoot_index, shooting, shoot_timer, shoot_cooldown
    global enemy_spawn_timer, score, game_over
    speed = 5
    moving = False

    if keyboard.left and player.x > 30:
        player.x -= speed
        player.direction = "left"
        moving = True
    elif keyboard.right and player.x < WIDTH - 30:
        player.x += speed
        player.direction = "right"
        moving = True

    level_shoot_cooldown = max(1, BASE_SHOOT_COOLDOWN - (player.level * 2))
    
    if shoot_cooldown <= 0:
        shoot()
        shoot_cooldown = level_shoot_cooldown
    else:
        shoot_cooldown -= 1

    update_gun_position()
    update_shooting_animation()
    update_player_animation(moving)
    update_bullets()
    
    enemy_spawn_timer -= 1
    if enemy_spawn_timer <= 0:
        spawn_enemy()
        enemy_spawn_timer = random.randint(30, 100)

    update_enemies_state()
    check_collisions()

def update_enemies_state():
    global game_over
    
    enemies_to_remove = []
    
    for enemy in enemies:
        if enemy.update():
            game_over = True

        if abs(enemy.speed) <= 0.1:
            enemies_to_remove.append(enemy)

    for enemy in enemies_to_remove:
        if enemy in enemies:
            enemies.remove(enemy)

def update_gun_position():
    gun.x = player.x
    gun.y = player.y - 20
    gun.angle = 90

def update_shoot_effect_position():
    shoot_effect.x = gun.x
    shoot_effect.y = gun.y - 30
    shoot_effect.angle = 270

def update_shooting_animation():
    global shooting, shoot_timer, shoot_index
    
    if shooting:
        shoot_effect.image = shoot_frames[shoot_index]
        shoot_effect.visible = True

        update_shoot_effect_position()
            
        shoot_index = (shoot_index + 1) % len(shoot_frames)

        shoot_timer -= 1
        if shoot_timer <= 0:
            shooting = False
            shoot_index = 0
            shoot_effect.visible = False

def update_player_animation(moving):
    global frame_index
    
    if moving:
        player.state = "running"
        frame_index = (frame_index + 0.2) % len(run_frames)
        player.image = run_frames[int(frame_index)]
    else:
        player.state = "idle"
        frame_index = (frame_index + 0.2) % len(run_frames)
        player.image = idle_frames[int(frame_index)]

def update_bullets():
    for bullet in bullets:
        bullet.y -= 8
    
    bullets[:] = [b for b in bullets if b.y > 0]

def shoot():
    global shooting, shoot_timer

    bullet = Actor("1", (gun.x, gun.y - 20))
    bullets.append(bullet)

    shooting = True
    shoot_timer = len(shoot_frames)

def spawn_enemy():
    if len(enemies) % 20 == 0:
        enemy = Enemy("asteroid_prize", (random.randint(50, WIDTH - 50), 0))
        enemy.is_prize = True
    else:
        enemy = Enemy("asteroid_small", (random.randint(50, WIDTH - 50), 0))
    enemies.append(enemy)
    if sound_enabled:
        sounds.score.play(1)

def check_collisions():
    global score
    
    bullets_to_remove = set()

    level_bullet_damage = BASE_BULLET_DAMAGE + (player.level * 10)
    
    for i, bullet in enumerate(bullets):
        for enemy in enemies:
            if bullet.colliderect(enemy):
                bullets_to_remove.add(i)
                if sound_enabled:
                    sounds.hit.play(1)
                if enemy.take_damage(level_bullet_damage):
                    if enemy.is_prize:
                        score += 100
                        player.gain_xp(100)
                    else:
                        enemy_score = 10 * (enemy.bounce_count + 1)
                        score += enemy_score
                        player.gain_xp(enemy_score)
                    enemies.remove(enemy)
                break
    
    for i in sorted(bullets_to_remove, reverse=True):
        if i < len(bullets):
            bullets.pop(i)

def reset_game():
    global score, game_over, enemies, bullets, enemy_spawn_timer
    
    score = 0
    game_over = False
    enemies = []
    bullets = []
    enemy_spawn_timer = 60
    
    player.pos = (400, GROUND_Y - 25)
    player.level = 1
    player.xp = 0
    player.xp_needed = 4
    player.max_health = 100
    player.health = 100

def on_mouse_down(pos):
    global game_state, sound_enabled
    
    if game_state == "menu":
        if start_button.collidepoint(pos):
            game_state = "playing"
            reset_game()
        elif sound_button.collidepoint(pos):
            sound_enabled = not sound_enabled
        elif quit_button.collidepoint(pos):
            exit()
    
    elif game_state == "paused":
        if resume_button.collidepoint(pos):
            game_state = "playing"
        elif pause_sound_button.collidepoint(pos):
            sound_enabled = not sound_enabled
        elif pause_quit_button.collidepoint(pos):
            exit()

def on_key_down(key):
    global game_state
    
    if key == keys.ESCAPE:
        if game_state == "playing":
            game_state = "paused"
        elif game_state == "paused":
            game_state = "playing"

pgzrun.go()