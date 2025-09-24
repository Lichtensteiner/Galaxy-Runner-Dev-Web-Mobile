import pygame
import random
import sys

pygame.init()
pygame.mixer.init()

# Fenêtre
WIDTH, HEIGHT = 600, 800
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Galaxy Runner Dev Web & Mobile")

# Couleurs
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)

# Polices
FONT = pygame.font.SysFont("comicsans", 15)
BIG_FONT = pygame.font.SysFont("comicsans", 30)

# Icônes / Stickers simples
ICON_DEBUTANT = pygame.Surface((40,40)); ICON_DEBUTANT.fill(GREEN)
ICON_NORMAL = pygame.Surface((40,40)); ICON_NORMAL.fill(YELLOW)
ICON_PRO = pygame.Surface((40,40)); ICON_PRO.fill(RED)
ICON_PLAY = pygame.Surface((40,40)); ICON_PLAY.fill(GREEN)
ICON_PAUSE = pygame.Surface((40,40)); ICON_PAUSE.fill(RED)
ICON_QUIT = pygame.Surface((40,40)); ICON_QUIT.fill(GRAY)
ICON_LOST = pygame.Surface((60,60)); ICON_LOST.fill(RED) # sticker "perdu"

# Images du jeu
SHIP_IMG = pygame.Surface((50,50)); SHIP_IMG.fill(BLUE)
ASTEROID_IMG = pygame.Surface((50,50)); ASTEROID_IMG.fill(RED)
BONUS_IMG = pygame.Surface((30,30)); BONUS_IMG.fill(YELLOW)

# Musique
pygame.mixer.music.load("./Musique/music.mp3")

# Classes
class Player:
    def __init__(self):
        self.image = SHIP_IMG
        self.rect = self.image.get_rect(center=(WIDTH//2, HEIGHT-100))
        self.speed = 7
        self.shield = False

    def move(self, keys):
        dx = dy = 0
        if keys[pygame.K_LEFT]: dx = -self.speed
        if keys[pygame.K_RIGHT]: dx = self.speed
        if keys[pygame.K_UP]: dy = -self.speed
        if keys[pygame.K_DOWN]: dy = self.speed
        if keys[pygame.K_LSHIFT]: dx*=1.5; dy*=1.5
        self.rect.x += dx; self.rect.y += dy
        self.rect.left = max(self.rect.left,0)
        self.rect.right = min(self.rect.right,WIDTH)
        self.rect.top = max(self.rect.top,0)
        self.rect.bottom = min(self.rect.bottom,HEIGHT)

    def draw(self, win):
        win.blit(self.image, self.rect)
        if self.shield: pygame.draw.ellipse(win,GREEN,self.rect.inflate(20,20),3)

class Asteroid:
    def __init__(self, speed_min, speed_max):
        size=random.randint(30,70)
        self.image=pygame.Surface((size,size)); self.image.fill(RED)
        self.rect=self.image.get_rect(center=(random.randint(25,WIDTH-25),-50))
        self.speed=random.randint(speed_min,speed_max)
    def move(self): self.rect.y += self.speed
    def draw(self,win): win.blit(self.image,self.rect)

class Bonus:
    def __init__(self):
        self.image=BONUS_IMG
        self.rect=self.image.get_rect(center=(random.randint(15,WIDTH-15),-30))
        self.speed=5
        self.type=random.choice(["shield","points","boost"])
    def move(self): self.rect.y += self.speed
    def draw(self,win): win.blit(self.image,self.rect)

class Button:
    def __init__(self,x,y,w,h,color,text,icon=None):
        self.rect=pygame.Rect(x,y,w,h)
        self.color=color
        self.text=text
        self.icon=icon
    def draw(self,win):
        pygame.draw.rect(win,self.color,self.rect)
        txt=FONT.render(self.text,True,BLACK)
        win.blit(txt,(self.rect.x+50,self.rect.y+10))
        if self.icon: win.blit(self.icon,(self.rect.x+5,self.rect.y+5))
    def is_clicked(self,pos): return self.rect.collidepoint(pos)

# Dessin jeu
def draw_window(player,asteroids,bonuses,score,stars,pause_btn,quit_btn):
    WIN.fill(BLACK)
    for star in stars:
        pygame.draw.circle(WIN,WHITE,(star[0],star[1]),star[2])
        star[1]+=star[3]
        if star[1]>HEIGHT: star[1]=0; star[0]=random.randint(0,WIDTH)
    player.draw(WIN)
    for a in asteroids: a.draw(WIN)
    for b in bonuses: b.draw(WIN)
    WIN.blit(FONT.render(f"Score: {score}",True,WHITE),(10,10))
    pause_btn.draw(WIN)
    quit_btn.draw(WIN)
    pygame.display.update()

# Boucle principale
def main(level_speed=(3,8), spawn_interval=20, current_score=0):
    pygame.mixer.music.play(-1)
    clock=pygame.time.Clock()
    run=True
    paused=False
    player=Player()
    asteroids=[]
    bonuses=[]
    score=current_score
    spawn_timer=0
    bonus_timer=0
    stars=[[random.randint(0,WIDTH), random.randint(0,HEIGHT),
           random.randint(1,3), random.randint(1,3)] for _ in range(50)]
    pause_btn=Button(WIDTH-180,10,80,40,GRAY,"Pause",ICON_PAUSE)
    quit_btn=Button(WIDTH-90,10,80,40,GRAY,"Quitter",ICON_QUIT)

    while run:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type==pygame.QUIT: pygame.quit(); sys.exit()
            if event.type==pygame.MOUSEBUTTONDOWN:
                if pause_btn.is_clicked(event.pos):
                    paused=not paused
                    pause_btn.icon=ICON_PLAY if paused else ICON_PAUSE
                    pause_btn.text="Play" if paused else "Pause"
                if quit_btn.is_clicked(event.pos):
                    pygame.mixer.music.stop()
                    main_menu()

        keys=pygame.key.get_pressed()
        if not paused:
            player.move(keys)
            spawn_timer+=1
            bonus_timer+=1

            if spawn_timer>spawn_interval: asteroids.append(Asteroid(*level_speed)); spawn_timer=0
            if bonus_timer>200: bonuses.append(Bonus()); bonus_timer=0

            for a in asteroids[:]:
                a.move()
                if a.rect.top>HEIGHT: asteroids.remove(a); score+=1
                if a.rect.colliderect(player.rect):
                    if player.shield: player.shield=False; asteroids.remove(a)
                    else:
                        pygame.mixer.music.stop()
                        game_over(score)
                        return

            for b in bonuses[:]:
                b.move()
                if b.rect.top>HEIGHT: bonuses.remove(b)
                if b.rect.colliderect(player.rect):
                    if b.type=="shield": player.shield=True
                    elif b.type=="points": score+=10
                    elif b.type=="boost": player.boost=True
                    bonuses.remove(b)
        draw_window(player,asteroids,bonuses,score,stars,pause_btn,quit_btn)

# Écran de fin
def game_over(score):
    continue_btn=Button(150,400,300,60,GREEN,"Continuez")
    restart_btn=Button(150,500,300,60,YELLOW,"Reprendre")
    quit_btn=Button(150,600,300,60,GRAY,"Quitter")

    run=True
    while run:
        WIN.fill(BLACK)
        lost_text=BIG_FONT.render("Vous avez perdu cher ami !",True,RED)
        WIN.blit(lost_text,(WIDTH//2 - lost_text.get_width()//2,150))
        WIN.blit(ICON_LOST,(WIDTH//2 - ICON_LOST.get_width()//2,250))
        score_text=FONT.render(f"Score final: {score}",True,WHITE)
        WIN.blit(score_text,(WIDTH//2 - score_text.get_width()//2,350))
        continue_btn.draw(WIN); restart_btn.draw(WIN); quit_btn.draw(WIN)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type==pygame.QUIT: pygame.quit(); sys.exit()
            if event.type==pygame.MOUSEBUTTONDOWN:
                pos=event.pos
                if continue_btn.is_clicked(pos): main(current_score=score); return
                if restart_btn.is_clicked(pos): main(current_score=0); return
                if quit_btn.is_clicked(pos): main_menu(); return

# Menu principal
def main_menu():
    run=True
    btn_debutant=Button(150,300,300,60,GREEN,"Débutant",ICON_DEBUTANT)
    btn_normal=Button(150,400,300,60,YELLOW,"Normal",ICON_NORMAL)
    btn_pro=Button(150,500,300,60,RED,"Professionnel",ICON_PRO)
    btn_quit=Button(150,600,300,60,GRAY,"Quitter",ICON_QUIT)

    # Message règles du jeu
    rules=["Utilisez les flèches pour déplacer le vaisseau.",
           "Évitez les astéroïdes et collectez les bonus.",
           "Shift pour booster la vitesse temporairement.",
           "Vous perdez si vous touchez un astéroïde sans bouclier."]

    while run:
        WIN.fill(BLACK)
        title=BIG_FONT.render("Galaxy Runner Dev Web & Mobile", True,WHITE)
        WIN.blit(title,(WIDTH//2 - title.get_width()//2,50))
        # Affichage des règles
        for i,line in enumerate(rules):
            txt=FONT.render(line,True,WHITE)
            WIN.blit(txt,(50,150 + i*40))

        btn_debutant.draw(WIN); btn_normal.draw(WIN); btn_pro.draw(WIN); btn_quit.draw(WIN)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type==pygame.QUIT: pygame.quit(); sys.exit()
            if event.type==pygame.MOUSEBUTTONDOWN:
                pos=event.pos
                if btn_debutant.is_clicked(pos): main(level_speed=(2,5), spawn_interval=30)
                if btn_normal.is_clicked(pos): main(level_speed=(3,8), spawn_interval=20)
                if btn_pro.is_clicked(pos): main(level_speed=(5,12), spawn_interval=15)
                if btn_quit.is_clicked(pos): pygame.quit(); sys.exit()

main_menu()
