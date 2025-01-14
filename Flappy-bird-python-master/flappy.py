import os
import random

import neat
import pygame

pygame.init()

#VARIABLES
pygame.font.init()
STAT_FONT = pygame.font.SysFont("comicsans", 50)
SCREEN_WIDHT = 600
SCREEN_HEIGHT = 800
FLOOR = 730
GROUND_WIDHT = 2 * SCREEN_WIDHT
GROUND_HEIGHT = 100
GAME_TICK_SPEED = 30
OBJECT_SPEED = 5

DRAW_LINES = False

# Images
background_day_img = pygame.transform.scale(pygame.image.load(os.path.join("assets", "sprites", "background-day.png")), (SCREEN_WIDHT, SCREEN_HEIGHT))
green_pipe_img = pygame.transform.scale2x(pygame.image.load(os.path.join("assets", "sprites", "pipe-green.png")))
red_pipe_img = pygame.transform.scale2x(pygame.image.load(os.path.join("assets", "sprites", "pipe-red.png")))
blue_bird_images = [pygame.transform.scale2x(pygame.image.load(os.path.join("assets", "sprites", f"bluebird-{flap}.png"))) for flap in ["upflap", "midflap", "downflap"]]
red_bird_images = [pygame.transform.scale2x(pygame.image.load(os.path.join("assets", "sprites", f"redbird-{flap}.png"))) for flap in ["upflap", "midflap", "downflap"]]
yellow_bird_images = [pygame.transform.scale2x(pygame.image.load(os.path.join("assets", "sprites", f"yellowbird-{flap}.png"))) for flap in ["upflap", "midflap", "downflap"]]
ground_img = pygame.transform.scale2x(pygame.image.load(os.path.join("assets", "sprites", "base.png")))

SCREEN = pygame.display.set_mode((SCREEN_WIDHT, SCREEN_HEIGHT))
gen = 0

# Music
wing = 'assets/audio/wing.wav'
hit = 'assets/audio/hit.wav'
pygame.mixer.init()

class Bird:
    MAX_ROTATION = 25
    ROT_VEL = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        self.images = blue_bird_images
        self.image_counter = 0
        self.x = x
        self.y = y
        self.tilt = 0  # degrees to tilt
        self.tick_count = 0
        self.speed = 0
        self.height = self.y
        self.img_count = 0
        self.current_image = self.images[0]

    def move(self):
        """
        make the bird move
        :return: None
        """
        self.tick_count += 1

        # for downward acceleration
        displacement = self.speed * self.tick_count + 0.5 * 3 * self.tick_count ** 2  # calculate displacement

        # terminal velocity
        if displacement >= 16:
            displacement = (displacement / abs(displacement)) * 16

        if displacement < 0:
            displacement -= 2

        self.y = self.y + displacement

        if displacement < 0 or self.y < self.height + 50:  # tilt up
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:  # tilt down
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL

    def bump(self):
        self.speed = -10.5
        self.tick_count = 0
        self.height = self.y

    def draw(self, win):
        """
        draw the bird
        :param win: pygame window or surface
        :return: None
        """
        self.img_count += 1

        # For animation of bird, loop through three images
        if self.img_count <= self.ANIMATION_TIME:
            self.current_image = self.images[0]
        elif self.img_count <= self.ANIMATION_TIME * 2:
            self.current_image = self.images[1]
        elif self.img_count <= self.ANIMATION_TIME * 3:
            self.current_image = self.images[2]
        elif self.img_count <= self.ANIMATION_TIME * 4:
            self.current_image = self.images[1]
        elif self.img_count == self.ANIMATION_TIME * 4 + 1:
            self.current_image = self.images[0]
            self.img_count = 0

        # so when bird is nose diving it isn't flapping
        if self.tilt <= -80:
            self.current_image = self.images[1]
            self.img_count = self.ANIMATION_TIME * 2

        # tilt the bird
        blitRotateCenter(win, self.current_image, (self.x, self.y), self.tilt)

    def get_mask(self):
        """
        gets the mask for the current image of the bird
        :return: None
        """
        return pygame.mask.from_surface(self.current_image)

    def next_image(self):
        if self.image_counter % 3 == 0:
            self.images = red_bird_images
        elif self.image_counter % 3 == 1:
            self.images = yellow_bird_images
        else:
            self.images = blue_bird_images
        self.image_counter += 1

pipe_counter = 0
class Pipe:
    GAP = 200

    def __init__(self, xpos: int):
        self.x = xpos
        self.height = 0

        self.top_height = 0
        self.bottom_height = 0

        # Decide pipe color
        global pipe_counter
        if pipe_counter % 2 == 0:
            self.image = green_pipe_img
        else:
            self.image = red_pipe_img
        pipe_counter += 1

        self.top = pygame.transform.flip(self.image, False, True)
        self.bottom = self.image

        self.passed = False

        self.set_height()

    def set_height(self):
        """
        set the height of the pipe, from the top of the screen
        :return: None
        """
        self.height = random.randrange(50, 450)
        self.top_height = self.height - self.top.get_height()
        self.bottom_height = self.height + self.GAP

    def update(self):
        self.x -= OBJECT_SPEED

    def draw(self, win):
        win.blit(self.top, (self.x, self.top_height))
        win.blit(self.bottom, (self.x, self.bottom_height))

    def collide(self, bird, win):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.top)
        bottom_mask = pygame.mask.from_surface(self.bottom)
        top_offset = (self.x - bird.x, self.top_height - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom_height - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)

        if b_point or t_point:
            return True # Collision detected

        return False # No collision detected


class Ground:
    WIDTH = ground_img.get_width()
    IMG = ground_img

    def __init__(self, y):
        self.image = pygame.image.load('assets/sprites/base.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (GROUND_WIDHT, GROUND_HEIGHT))

        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def update(self):
        """
                move floor so it looks like its scrolling
                :return: None
                """
        self.x1 -= OBJECT_SPEED
        self.x2 -= OBJECT_SPEED
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        """
        Draw the floor. This is two images that move together.
        :param win: the pygame surface/window
        :return: None
        """
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))


def blitRotateCenter(surf, image, topleft, angle):
    """
    Rotate a surface and blit it to the window
    :param surf: the surface to blit to
    :param image: the image surface to rotate
    :param topleft: the top left position of the image
    :param angle: a float value for angle
    :return: None
    """
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center=image.get_rect(topleft=topleft).center)

    surf.blit(rotated_image, new_rect.topleft)


def draw_window(win, birds, pipes, ground, score, pipe_ind):
    """
    draws the windows for the main game loop
    :param win: pygame window surface
    :param birds: a Bird object
    :param pipes: List of pipes
    :param ground: Ground object
    :param score: score of the game (int)
    :param gen: current generation
    :param pipe_ind: index of closest pipe
    :return: None
    """
    global gen
    if gen == 0:
        gen = 1
    win.blit(background_day_img, (0, 0))

    for pipe in pipes:
        pipe.draw(win)

    ground.draw(win)
    for bird in birds:
        # draw lines from bird to pipe
        if DRAW_LINES:
            try:
                pygame.draw.line(win, (255, 0, 0),
                                 (bird.x + bird.current_image.get_width() / 2, bird.y + bird.current_image.get_height() / 2),
                                 (pipes[pipe_ind].x + pipes[pipe_ind].PIPE_TOP.get_width() / 2, pipes[pipe_ind].height),
                                 5)
                pygame.draw.line(win, (255, 0, 0),
                                 (bird.x + bird.current_image.get_width() / 2, bird.y + bird.current_image.get_height() / 2),
                                 (pipes[pipe_ind].x + pipes[pipe_ind].PIPE_BOTTOM.get_width() / 2, pipes[pipe_ind].bottom),
                                 5)
            except:
                pass
        # draw bird
        bird.draw(win)

    # score
    score_label = STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))
    win.blit(score_label, (SCREEN_WIDHT - score_label.get_width() - 15, 10))

    # generations
    score_label = STAT_FONT.render("Gens: " + str(gen - 1), 1, (255, 255, 255))
    win.blit(score_label, (10, 10))

    # alive
    score_label = STAT_FONT.render("Alive: " + str(len(birds)), 1, (255, 255, 255))
    win.blit(score_label, (10, 50))

    pygame.display.update()


def eval_genomes(genomes, config):
    """
    runs the simulation of the current population of
    birds and sets their fitness based on the distance they
    reach in the game.
    """
    global SCREEN, gen
    win = SCREEN
    gen += 1

    # start by creating lists holding the genome itself, the
    # neural network associated with the genome and the
    # bird object that uses that network to play
    nets = []
    birds = []
    ge = []

    for genome_id, genome in genomes:
        genome.fitness = 0  # start with fitness level of 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        birds.append(Bird(230, 350))
        ge.append(genome)

    base = Ground(FLOOR)
    pipes = [Pipe(700)]
    score = 0

    clock = pygame.time.Clock()

    run = True
    while run and len(birds) > 0:
        clock.tick(GAME_TICK_SPEED)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        pipe_ind = 0
        if len(birds) > 0:
            # pipes[1] = PIPE_TOP?
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].top.get_width():  # determine whether to use the first or second
                pipe_ind = 1  # pipe on the screen for neural network input

        for x, bird in enumerate(birds):  # give each bird a fitness of 0.1 for each frame it stays alive
            ge[x].fitness += 0.1
            bird.move()

            # send bird location, top pipe location and bottom pipe location and determine from network whether to jump or not
            output = nets[birds.index(bird)].activate(
                (bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom_height)))

            if output[0] > 0.5:  # we use a tanh activation function so result will be between -1 and 1. if over 0.5 jump
                bird.bump()

        base.update()

        rem = []
        add_pipe = False
        for pipe in pipes:
            pipe.update()
            # check for collision
            for bird in birds:
                #if pygame.sprite.collide_rect(pipe, bird): win?
                if pipe.collide(bird, win):
                    ge[birds.index(bird)].fitness -= 1
                    nets.pop(birds.index(bird))
                    ge.pop(birds.index(bird))
                    birds.pop(birds.index(bird))

            if pipe.x + pipe.top.get_width() < 0:
                rem.append(pipe)

            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                add_pipe = True
                for bird in birds:
                    bird.next_image()


        if add_pipe:
            score += 1
            # can add this line to give more reward for passing through a pipe (not required)
            for genome in ge:
                genome.fitness += 5
            pipes.append(Pipe(SCREEN_WIDHT))

        for r in rem:
            pipes.remove(r)

        for bird in birds:
            if bird.y + bird.current_image.get_height() - 10 >= FLOOR or bird.y < -50:
                nets.pop(birds.index(bird))
                ge.pop(birds.index(bird))
                birds.pop(birds.index(bird))

        draw_window(SCREEN, birds, pipes, base, score, pipe_ind)

        # break if score gets large enough
        '''if score > 20:
            pickle.dump(nets[0],open("best.pickle", "wb"))
            break'''


def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
                                neat.DefaultStagnation, config_path)

    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(eval_genomes, 50)


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config_feedforward.txt")
    run(config_path)
