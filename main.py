import pygame
import os
import random as rn

SCR_WIDTH = 500
SCR_HEIGHT = 800

SPEED = 5

IMG_PIPE = pygame.transform.scale2x(pygame.image.load(os.path.join('assets', 'pipe.png')))
IMG_FLOOR = pygame.transform.scale2x(pygame.image.load(os.path.join('assets', 'floor.png')))
IMG_BG = pygame.transform.scale2x(pygame.image.load(os.path.join('assets', 'bg.png')))
IMGS_BIRD = [
    pygame.transform.scale2x(pygame.image.load(os.path.join('assets', 'bird1.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('assets', 'bird2.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('assets', 'bird3.png')))
]
pygame.font.init()
FONT_SCORE = pygame.font.SysFont('courier new', 38)

class Bird:
    IMAGES = IMGS_BIRD
    MAX_ROTATION = 25
    SPEED_ROTATION = 20
    ANIMATION_TIME = 1

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.speed = 0
        self.height = self.y
        self.time = 0
        self.img_i = 0
        self.img = self.IMAGES[0]

    def jump(self):
        self.speed = -8
        self.time = 0
        self.altura = self.y

    def offset(self):
        self.time += 1
        off_set = 1 * (self.time **2) + self.speed * self.time
        if off_set > 14:
            off_set = 14
        elif off_set < 0:
            off_set -= 2

        self.y += off_set

        if off_set < 0 or self.y < (self.height + 50):
            if self.angle < self.MAX_ROTATION:
                self.angle = self.MAX_ROTATION
        else:
            if self.angle > -90:
                self.angle -= self.SPEED_ROTATION

    def render(self, screen):
        self.img_i += 1
        if self.img_i < self.ANIMATION_TIME:
            self.img = self.IMAGES[0]
        elif self.img_i < self.ANIMATION_TIME * 2:
            self.img = self.IMAGES[1]
        elif self.img_i < self.ANIMATION_TIME * 3:
            self.img = self.IMAGES[2]
        elif self.img_i < self.ANIMATION_TIME * 4:
            self.img = self.IMAGES[1]
        elif self.img_i >= self.ANIMATION_TIME * 4 + 1:
            self.img = self.IMAGES[0]
            self.img_i = 0

        if self.angle <= -80:
            self.img = self.IMAGES[1]
            self.img_i = self.ANIMATION_TIME *2

        rot = pygame.transform.rotate(self.img, self.angle)
        center = self.img.get_rect(topleft=(self.x, self.y)).center
        rect = rot.get_rect(center=center)

        screen.blit(rot, rect.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)



class Pipe:
    GATE_DISTANCE = 250

    def __init__(self, x):
        self.x = x
        self.height = 0
        self.pos_upper = 0
        self.pos_lower = 0
        self.img_upper = pygame.transform.flip(IMG_PIPE, False, True)
        self.img_lower = IMG_PIPE
        self.obsolete = False
        self.set_height()

    def set_height(self):
        self.height = rn.randrange(int(SCR_HEIGHT/10), int(SCR_HEIGHT/2))
        self.pos_upper = self.height - self.img_upper.get_height()
        self.pos_lower = self.height + self.GATE_DISTANCE

    def offset(self):
        self.x -= SPEED

    def render(self, screen):
        screen.blit(self.img_upper, (self.x, self.pos_upper))
        screen.blit(self.img_lower, (self.x, self.pos_lower))

    def hit(self, bird):
        bird_mask = bird.get_mask()
        uper_mask = pygame.mask.from_surface(self.img_upper)
        lower_mask = pygame.mask.from_surface(self.img_lower)

        distance_upper = (self.x - bird.x, self.pos_upper - round(bird.y))
        distance_lower = (self.x - bird.x, self.pos_lower - round(bird.y))

        hit_point_upper = bird_mask.overlap(uper_mask, distance_upper)
        hit_point_lower = bird_mask.overlap(lower_mask, distance_lower)

        if hit_point_upper or hit_point_lower:
            return True
        else:
            return False
        


class Floor:
    WIDTH = IMG_FLOOR.get_width()
    IMG = IMG_FLOOR

    def __init__(self, y):
        self.y = y
        self.x_floor1 = 0
        self.x_floor2 = self.WIDTH

    def offset(self):
        self.x_floor1 -= SPEED
        self.x_floor2 -= SPEED

        if self.x_floor1 + self.WIDTH < 0:
            self.x_floor1 = self.x_floor2 + self.WIDTH

        if self.x_floor2 + self.WIDTH < 0:
            self.x_floor2 = self.x_floor1 + self.WIDTH

    def render(self, screen):
        screen.blit(self.IMG, (self.x_floor1, self.y))
        screen.blit(self.IMG, (self.x_floor2, self.y))


def render(screen, bird, pipes, floor, score):
    screen.blit(IMG_BG, (0, 0))

    bird.render(screen)

    for pipe in pipes:
        pipe.render(screen)
    
    score_text = FONT_SCORE.render(f"Score: {score}", 1, (255,255,255))
    screen.blit(score_text, (SCR_WIDTH - 10 - score_text.get_width(), 10))

    floor.render(screen)

    pygame.display.update()


def main():
    bird = Bird(50, int(SCR_HEIGHT / 3))
    floor = Floor(SCR_HEIGHT - int(IMG_FLOOR.get_height()/2))
    pipes = [Pipe(SCR_WIDTH)]
    screen = pygame.display.set_mode((SCR_WIDTH, SCR_HEIGHT))
    score = 0

    clock = pygame.time.Clock()

    running = True


    while running:
        clock.tick(30)

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
                pygame.quit()
                quit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_UP:
                    bird.jump()

        bird.offset()
        floor.offset()

        add_new_pipe = False
        pipes_to_remove = []

        for pipe in pipes:
            if pipe.hit(bird):
                running = False

            if not pipe.obsolete and bird.x > pipe.x:
                pipe.obsolete = True
                add_new_pipe = True
            pipe.offset()

            if pipe.x + pipe.img_upper.get_width() < 0:
                pipes_to_remove.append(pipe)
            
        if add_new_pipe:
            score += 1;
            global SPEED
            SPEED += 1
            pipes.append(Pipe(SCR_WIDTH * 1.1))

        for pipe in pipes_to_remove:
            pipes.remove(pipe)

        if bird.y + bird.img.get_height() > floor.y or bird.y < 0:
            running = False

        render(screen, bird, pipes, floor, score)



if __name__ == '__main__':
    main()