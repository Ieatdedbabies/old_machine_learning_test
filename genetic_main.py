import pygame as pg
import numpy as np
from math import *
from DNA import *
from random import *
import os
import sys
import ast
vec = pg.math.Vector2
os.environ["SDL_VIDEO_CENTERED"] = "1"


def collision(sprite, rect, line):
    if line[0] == line[2]:
        if rect.right >= line[0] >= rect.left and\
           (rect.bottom <= max(line[1], line[3]) or\
           rect.top >= min(line[1], line[3])):
            if sprite.rect.centerx > line[0]:
                sprite.pos = vec(line[0]+sprite.rect.width/2, sprite.pos.y)
                sprite.vel = vec(max(0, sprite.vel.x), sprite.vel.y)
            else:
                sprite.pos = vec(line[0]-sprite.rect.width/2, sprite.pos.y)
                sprite.vel = vec(min(0, sprite.vel.x), sprite.vel.y)
    elif line[1] == line[3]:
        if rect.bottom >= line[1] >= rect.top and\
           (rect.right <= max(line[0], line[2]) or\
           rect.left >= min(line[0], line[2])):
            if sprite.rect.centery < line[1]:
                sprite.pos = vec(sprite.pos.x, line[1]-sprite.rect.height/2)
                sprite.vel = vec(sprite.vel.x, min(0, sprite.vel.y))
            else:
                sprite.pos = vec(sprite.pos.x, line[1]+sprite.rect.height/2)
                sprite.vel = vec(sprite.vel.x, max(0, sprite.vel.y))

class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y, num):
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.image = pg.Surface((20,20))
        self.image.fill((128, 0, 128))
        self.rect = self.image.get_rect()
        self.game = game
        self.pos = vec(x,y)
        self.rect.center = self.pos
        self.num = num
        self.vel = vec(0,0)
        self.health = 5
        self.last_state = 0
        self.first_mvt = 0
        self.middle = vec(self.game.width/2, self.game.height/2)
        self.maxdist = (vec(0,0).distance_squared_to(self.middle) ** 2)/1000000000
        self.averagedist = self.maxdist - ((self.pos.distance_squared_to(self.middle)**2)/1000000000)

    def conditions(self):
        if self.num%2:
            enem = self.game.cubes[self.num-1]
        else:
            enem = self.game.cubes[self.num+1]
        if self.pos.x < enem.pos.x:
            eposx = 0
        else:
            eposx = 1
        if self.pos.y < enem.pos.y:
            eposy = 0
        else:
            eposy = 1
        if enem.vel.x < 0:
            evelx = -1
        elif enem.vel.x > 0:
            evelx = 1
        else:
            evelx = 0
        if enem.vel.y < 0:
            evely = -1
        elif enem.vel.y > 0:
            evely = 1
        else:
            evely = 0
        self.state = (eposx, eposy, evelx, evely)

    def movement(self):
        self.vel = vec(0,0)
        self.conditions()
        for condition in self.game.pop[self.num]:
            if self.state == condition[0]:
                if self.last_state != self.state:
##                    self.first_mvt = pg.time.get_ticks()
                    self.first_loop = self.game.loop
                self.last_state = self.state
                for i in xrange(len(condition)):
                    if not i:
                        tottime = 0
                    else:
##                        last_mvt = pg.time.get_ticks()
                        last_loop = self.game.loop
                        tottime += condition[i][2]
##                        if last_mvt - self.first_mvt > tottime*1000:
                        if last_loop - self.first_loop > tottime:
                            continue
                        self.vel.x = self.game.speed * condition[i][0]
                        self.vel.y = self.game.speed * condition[i][1]
                        break

    def update(self):
        self.movement()
        for line in self.game.lines:
            collision(self, self.rect, line)
        self.pos += self.vel
        self.rect.center = self.pos
        self.averagedist += (self.maxdist - ((self.pos.distance_squared_to(self.middle)**2)/1000000000))
        if self.game.reset:
            self.game.avrgdist[self.num] = self.averagedist
            fitness = self.averagedist/self.game.loop
            self.game.fitness[self.num] = fitness
            self.kill()
    

class game:
    def __init__(self):
        self.width = 800
        self.height = 600

        pg.init()
        self.screen = pg.display.set_mode((self.width, self.height))
######################################################################################################################################
        self.img = 1
        self.newpopulation = 0
######################################################################################################################################
        self.clock = pg.time.Clock()
        self.fps = 60

        self.black = (0,0,0)
        self.white = (255,255,255)
        self.red = (255,0,0)
        self.blue = (0,0,255)
        self.green = (0,255,0)
        self.yellow = (255,255,0)

        self.all_sprites = pg.sprite.Group()
        self.speed = 5

        bleft = (0,0,0,self.height)
        bright = (self.width,0,self.width,self.height)
        btop = (0,0,self.width,0)
        bbottom = (0,self.height,self.width,self.height)
        self.lines = (bleft, bright, btop, bbottom)
        self.running = True
        self.popamount = 500
        self.fitness = [0 for i in xrange(self.popamount)]
        self.avrgdist = [0 for i in xrange(self.popamount)]
        self.bestavrgdist = 0

    def gen0(self):
        if self.newpopulation:
            self.pop = newpop(self.popamount)
        else:
            with open("500pop.txt", "r") as f:
                self.pop = ast.literal_eval(f.readline().rstrip())
        self.reset = False
        self.cubes = [Player(self, self.width*(abs((i%2)-0.2)), self.height*(abs((i%2)-0.2)), i) for i in xrange(self.popamount)]
        self.gen = 0
        self.loop = 0

    def Reset(self):
        self.reset = False
        self.loop = 0
        self.breeding()
        self.cubes = [Player(self, self.width*(abs((i%2)-0.2)), self.height*(abs((i%2)-0.2)), i) for i in xrange(self.popamount)]
            
    def breeding(self):
        self.newavrgdist = sum(self.avrgdist)/self.popamount
        self.sum = sum(self.fitness)
        self.perc = [self.fitness[i]/self.sum for i in xrange(len(self.fitness))]
        self.prnt = 1
        self.lastgen = self.pop
        self.lastperc = self.perc
        if self.newavrgdist > self.bestavrgdist:
            self.bestavrgdist = self.newavrgdist
            self.bestperc = self.perc
            bestgen = str(self.pop)
            file = open("best_DNA.txt", "w")
            file.write(bestgen)
            file.close()
            print "best"
            file = open("best_DNA_fitness.txt", "w")
            file.write(str(self.fitness))
            file.close()
        self.couples = []
        for couple in xrange(len(self.perc)):
            parent1 = int(np.random.choice(len(self.perc), p=self.perc))
            parent2 = int(np.random.choice(len(self.perc), p=self.perc))
            while parent1 == parent2:
                parent2 = int(np.random.choice(len(self.perc), p=self.perc))
            self.couples.append((parent1, parent2))
        newpop = []
        for couple in self.couples:
            child = []
            for dna in xrange(len(self.pop[0])):
                gene = []
                gene.append(self.pop[0][dna][0])
                genome = round((( (len(self.pop[couple[0]][dna])) -1) + ( (len(self.pop[couple[1]][dna])) -1))/2)
                for genes in xrange(int(floor(genome/2))):
                    if random() < 0.000:
                        mvtx = randint(-1,1)
                        mvty = randint(-1,1)
                        time = randint(5,20)##########################################################################################
                        gene.append((mvtx,mvty,time))
                    else:
                        temp = randint(1, (len(self.pop[couple[1]][dna]))-1)
                        gene.append(self.pop[couple[1]][dna][temp])
                for genes in xrange(int(ceil(genome/2))):
                    if random() < 0.005:
                        mvtx = randint(-1,1)
                        mvty = randint(-1,1)
                        time = randint(5,20)##########################################################################################
                        gene.append((mvtx,mvty,time))
                    else:
                        temp = randint(1, (len(self.pop[couple[0]][dna]))-1)
                        gene.append(self.pop[couple[0]][dna][temp])
                child.append(gene)
            newpop.append(child)
        self.pop = newpop
        self.fitness = [0 for i in xrange(self.popamount)]
##        if self.prnt:
        print int(self.sum/self.popamount),  ",  ", self.gen
        self.gen += 1
##            print self.bestavrgdist
        if self.gen == 0:
            print self.newavrgdist
            lastgen = str(self.pop)
            file = open("saved_DNA.txt", "w")
            file.write(lastgen)
            file.close()
            self.running = False
            pg.quit()
            sys.exit()
        self.avrgdist = [0 for i in xrange(self.popamount)]
        
    def run(self):
        if self.running:
            self.gen0()
        self.running = True
        if self.reset:
            self.Reset()
        while self.running:
            self.clock.tick(0)
            self.mouse_pos = vec(pg.mouse.get_pos())
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                    pg.quit()
                    sys.exit()
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        self.running = False
                        pg.quit()
                        sys.exit()
                    if event.key == pg.K_r:
                        self.reset = True
                        self.running = False
                    if event.key == pg.K_SPACE:
                        self.img = not self.img
                        if not self.img:
                            self.screen.fill(self.black)
            if self.loop >= 800:
                self.reset = True
                self.running = False
            self.all_sprites.update()
            if self.img:
                self.screen.fill(self.white)
                for sprite in self.all_sprites:
                    self.screen.blit(sprite.image, sprite.rect)
            pg.display.set_caption("{:.2f}".format(self.clock.get_fps()))
            pg.display.flip()
            self.loop += 1

g = game()
while True:
    g.run()
