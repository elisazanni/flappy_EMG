import pygame, sys, random, os

#TENERE LISTA GLOBALE PUNTEGGI MIGLIORI
HIGH_SCORES = []
HIGH_SCORE_FILE = "highscores.txt"
MAX_HIGH_SCORES = 10

def load_high_scores():
    global HIGH_SCORES
    try:
        with open(HIGH_SCORE_FILE, "r") as f:
            scores = [int(line.strip()) for line in f if line.strip().isdigit()]
            scores.sort(reverse=True)
            HIGH_SCORES = scores[:MAX_HIGH_SCORES]
    except FileNotFoundError:
        HIGH_SCORES = []
    except Exception as e:
        print(f"Errore nel caricamento dei punteggi: {e}")
        HIGH_SCORES = []

def save_high_scores():
    try:
        with open(HIGH_SCORE_FILE, "w") as f:
            for s in HIGH_SCORES:
                f.write(f"{s}\n")
    except Exception as e:
        print(f"Errore nel salvataggio dei punteggi: {e}")

def update_high_scores(new_score):
    global HIGH_SCORES
    if new_score > 0:
        HIGH_SCORES.append(new_score)
        HIGH_SCORES.sort(reverse=True)
        HIGH_SCORES = HIGH_SCORES[:MAX_HIGH_SCORES]
        save_high_scores()
        
        
        

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


def display_game_over_screen():
    game_over_text = game_font.render("GAME OVER", True, (255, 0, 0))
    game_over_rect = game_over_text.get_rect(center=(288, 200))
    screen.blit(game_over_text, game_over_rect)

    high_score_title = game_font.render("HIGHEST SCORES", True, (255, 255, 255))
    high_score_rect = high_score_title.get_rect(center=(288, 300))
    screen.blit(high_score_title, high_score_rect)
    
    y_pos = 350
    for i, s in enumerate(HIGH_SCORES):
        color = (255, 255, 255)
        # EVIDENZIO IL PUNTEGGIO SE è IL TUO
        if s == int(score) and i == HIGH_SCORES.index(s):
            color = (255, 255, 0)

        score_line = f"{i + 1}. {s}"
        score_surface = game_font.render(score_line, True, color)
        score_rect = score_surface.get_rect(center=(288, y_pos)) 
        screen.blit(score_surface, score_rect)
        y_pos += 40 #spazio tra le linee

    restart_text = game_font.render("Premi SPAZIO per Riprovare", True, (255, 255, 255))
    restart_rect = restart_text.get_rect(center=(288, 800))
    screen.blit(restart_text, restart_rect)
    
    



####################################################################################
pygame.init()
load_high_scores() 

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
        new_game_active_state = check_collision(pipe_list) 
        
        if game_active and not new_game_active_state:
            # IL GIOCO E' APPENA FINITO
            update_high_scores(int(score))
        
        game_active = new_game_active_state
        
        pipe_list = move_pipes(pipe_list)
        draw_pipes(pipe_list)
    else:
        #STATO GAME OVER
        screen.blit(bird_surface, bird_rect) 
        
        # Chiama la funzione per disegnare la schermata del Game Over
        display_game_over_screen()


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