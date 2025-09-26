import pygame, sys, random, os

score = 0

def read_emg_state_from_file():
    file_path = "emg_state.txt"
    if not os.path.exists(file_path):
        return False 
    try:
        with open(file_path, "r") as f:
            state_str = f.read().strip()
            return state_str.lower() == "true"
    except IOError as e:
        print(f"Errore nella lettura del file: {e}")
        return False

def draw_floor():
    screen.blit(floor_surface, (floor_x_pos, 900))
    screen.blit(floor_surface, (floor_x_pos + 576, 900))

def create_pipe():
    random_pipe_pos = random.choice(pipe_height)
    # DISTANZA TRA TUBI A DX E SX (700 POCO?)
    bottom_pipe = pipe_surface.get_rect(midtop=(700, random_pipe_pos))
    # DISTANZA TRA TUBO SU E TUBO GIU' A 400 PIXEL (MOLTO LONTANI)
    top_pipe = pipe_surface.get_rect(midbottom=(700, random_pipe_pos - 400)) 
    return bottom_pipe, top_pipe

def move_pipes(pipes):
    for pipe in pipes:
        pipe.centerx -= 5 * game_speed_factor
    visible_pipes = [pipe for pipe in pipes if pipe.right > -50]
    return visible_pipes

def draw_pipes(pipes):
    for pipe in pipes:
        if pipe.bottom >= 1024:
            screen.blit(pipe_surface, pipe)
        else:
            flip_pipe = pygame.transform.flip(pipe_surface, False, True)
            screen.blit(flip_pipe, pipe)

def check_collision(pipes):
    for pipe in pipes:
        if bird_rect.colliderect(pipe):
            return False

    #condizione di "morte" se si colpisce il pavimento (>= 900) o si esce sopra (<= -100)
    if bird_rect.top <= -100 or bird_rect.bottom >= 900:
        
        return False
    return True

pygame.init()
screen = pygame.display.set_mode((576, 1024))
clock = pygame.time.Clock()
try:
    game_font = pygame.font.Font('04B_19.ttf',40)
except pygame.error:
    game_font = pygame.font.SysFont('arial', 40)

gravity = 0.3
bird_movement = 0
game_active = False
can_score = True

game_speed_factor = 0.5  # VELOCITA' DEL GIOCO

bg_surface = pygame.image.load('assets/background-day.png').convert()
bg_surface = pygame.transform.scale2x(bg_surface)

floor_surface = pygame.image.load('assets/base.png').convert()
floor_surface = pygame.transform.scale2x(floor_surface)
floor_x_pos = 0

bird_surface = pygame.image.load('assets/bluebird-midflap.png').convert_alpha()
bird_surface = pygame.transform.scale2x(bird_surface)
bird_rect = bird_surface.get_rect(center=(100, 512))

pipe_surface = pygame.image.load('assets/pipe-green.png')
pipe_surface = pygame.transform.scale2x(pipe_surface)
pipe_list = []
SPAWNPIPE = pygame.USEREVENT
# La velocità di spawn dei tubi viene ridotta in base al fattore di velocità
pygame.time.set_timer(SPAWNPIPE, int(1500 / game_speed_factor))
pipe_height = [400, 600, 800]

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if game_active:
                    bird_movement = 0
                    bird_movement -=9
                else:
                    # RIAVVIO (reset di tutto)
                    game_active = True
                    pipe_list.clear()
                    bird_rect.center = (100,512)
                    bird_movement = 0
                    score = 0 
        
        if event.type == SPAWNPIPE and game_active:
            pipe_list.extend(create_pipe())
            score +=1

    #LEGGO IL FILE EMG CON LO STATO
    if read_emg_state_from_file():
        if game_active:
            bird_movement = 0
            bird_movement -= 6      #QUANTO SALTARE
        else:
            game_active = True
            pipe_list.clear()
            bird_rect.center = (100, 512)
            bird_movement = 0
            score = 0
            
    screen.blit(bg_surface, (0, 0))

    if game_active:
        bird_movement += gravity
        bird_rect.centery += bird_movement
        screen.blit(bird_surface, bird_rect)
        
        game_active = check_collision(pipe_list) 
        
        pipe_list = move_pipes(pipe_list)
        draw_pipes(pipe_list)

    if game_active:
        floor_x_pos -= 1 * game_speed_factor
    
    draw_floor()
    if floor_x_pos <= -576:
        floor_x_pos = 0

    score_surface = game_font.render(str(int(score)),True,(255,255,255))
    score_rect = score_surface.get_rect(center = (288,100))
    screen.blit(score_surface,score_rect)
    
    
    pygame.display.update()
    # Rallenta il clock in base al fattore di velocità
    clock.tick(120 * game_speed_factor)