import pygame
import neat
import math
import random
import sys
from PIL import Image

class Car():
	def __init__(self,i):
		colors_radar = [
			(255,0,255),
			(0,255,0),
			(0,0,255),
			(255,100,0),
			(255,255,0),
			(255,0,0),
			(0,255,255)
		]
		self.img = pygame.image.load('car'+str(i)+'.png')	
		self.img = pygame.transform.scale(self.img,(self.img.get_width()//20,self.img.get_height()//20))
		self.rot_img = self.img
		self.size = [self.img.get_width(),self.img.get_height()]
		self.angle = 0
		self.speed = 5
		self.pos = [700,600]
		self.center = [self.pos[0]+self.img.get_width()//2,self.pos[1]+self.img.get_height()//2]
		self.radars = []
		self.is_alive = True
		self.score = 0
		self.color_radar = colors_radar[i]

	def rotate_img(self):
		self.rot_img = pygame.transform.rotate(self.img,self.angle)

	def check_collision(self):
		lw = self.img.get_width()
		lh = self.img.get_height()
		length = ((lw//10*5)**2+(lh//10*5)**2)**.5
		dots = [
			(self.center[0] - int(length*math.cos(math.radians(360 - self.angle - 20))),\
			self.center[1] - int(length*math.sin(math.radians(360 - self.angle - 20)))),
			(self.center[0] - int(length*math.cos(math.radians(self.angle - 20))),\
			self.center[1] + int(length*math.sin(math.radians(self.angle - 20)))),
			(self.center[0] + int(length*math.cos(math.radians(self.angle - 20))),\
			self.center[1] - int(length*math.sin(math.radians(self.angle - 20)))),
			(self.center[0] + int(length*math.cos(math.radians(360 - self.angle - 20))),\
			self.center[1] + int(length*math.sin(math.radians(360 - self.angle - 20))))
		]
		for dot in dots:
			# pygame.draw.circle(win,[200,30,230],dot,2)
			if road.get_at((dot[0],dot[1])) == (180,255,115,255):
				self.is_alive = False

	def check_radars(self):
		self.radars = []
		for degree in [-60,-30,0,30,60]:
			length = 0
			while length < 300:
				x = self.center[0] + int(length*math.cos(math.radians(degree-self.angle)))
				y = self.center[1] + int(length*math.sin(math.radians(degree-self.angle)))
				if road.get_at((x,y)) == (180,255,115,255):
					break
				length += 1
			self.radars.append([(x,y),length])
	
	def drive(self):
		self.pos[0] += int(self.speed*math.cos(math.radians(360 - self.angle)))
		self.pos[1] += int(self.speed*math.sin(math.radians(360 - self.angle)))
		self.center = [self.pos[0]+self.img.get_width()//2,self.pos[1]+self.img.get_height()//2]
		self.score += self.speed

	def draw_car(self,win):
		win.blit(self.rot_img,(self.center[0]-self.rot_img.get_width()//2,self.center[1]-self.rot_img.get_height()//2))

	def draw_radars(self,win):
		for radar in self.radars:
			pygame.draw.line(win,self.color_radar,self.center,radar[0],2)
			pygame.draw.circle(win,self.color_radar,radar[0],4)

	def get_data(self):
		ret = [0,0,0,0,0]
		for i in range(len(self.radars)):
			ret[i] = self.radars[i][1]//30
		
		return ret
	
	def turn(self,i,nets):
		a = nets[i].activate(self.get_data())	
		a = a.index(max(a))
		if a == 0:
			self.angle += 2
		else:
			self.angle -= 2

def print_text(win,generation,cars,best):
	font = pygame.font.SysFont('Comic Sans MS', 50)
	text = font.render('Generation : %d' % (generation), True, (0, 0, 0))
	text_rect = text.get_rect()
	text_rect.center = (road.get_width() - 200, 100)
	win.blit(text, text_rect)

	font = pygame.font.SysFont('Comic Sans MS', 30)
	text = font.render('Cars : %d' % (cars), True, (0, 0, 0))
	text_rect = text.get_rect()
	text_rect.center = (200, road.get_height() - 100)
	win.blit(text, text_rect)

	text = font.render('Best score : %d' % (best), True, (0, 0, 0))
	text_rect = text.get_rect()
	text_rect.center = (200, road.get_height() - 50)
	win.blit(text, text_rect)

def start(genomes,config):
	cars = []
	nets = []
	global generation
	generation += 1
	global best_score

	for i, g in genomes:
		net = neat.nn.FeedForwardNetwork.create(g, config)
		nets.append(net)
		g.fitness = 0

		cars.append(Car(i%7))

	run = True
	while run:
		win.blit(road,(0,0))
		n_best_score = max(car.score for car in cars)
		if n_best_score > best_score:
			best_score = n_best_score
				
		
		alive_cars = 0
		for i,car in enumerate(cars):
			if car.is_alive:
				alive_cars += 1
				car.drive()
				car.check_radars()				
				car.turn(i,nets)
				car.rotate_img()
				car.check_collision()
				car.draw_car(win)
				car.draw_radars(win)
				genomes[i][1].fitness += car.score/50

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				sys.exit()

		print_text(win,generation,alive_cars,best_score)
		
		if alive_cars == 0:
			run = False

		for i in range(len(trees)):
			win.blit(trees[i],tree_coords[i])
		
		pygame.display.update()	
			

pygame.init()
road = pygame.image.load('road.png')
road = pygame.transform.scale(road,(road.get_width()//3*2,road.get_height()//3*2))
win = pygame.display.set_mode((road.get_width(),road.get_height()))
pygame.display.set_caption('Cars')
cars = []
nets = []
trees = [pygame.image.load('tree'+str(i)+'.png') for i in range(8)]
trees = [pygame.transform.scale(tree,(120,120)) for tree in trees]
tree_coords = [
	(500,580),
	(900,170),
	(700,300),
	(800,450),
	(10,10),
	(300,500),
	(30,400),
	(300,300)
]
generation = 0
best_score = 0

config_path = "./config-feedforward.txt"
config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

p = neat.Population(config)

p.add_reporter(neat.StdOutReporter(True))
stats = neat.StatisticsReporter()
p.add_reporter(stats)

# p.run(start, 1000)
while True:
	for event in pygame.event.get():
			if event.type == pygame.QUIT:
				sys.exit()
			if event.type == pygame.KEYDOWN:
					p.run(start, 1000)