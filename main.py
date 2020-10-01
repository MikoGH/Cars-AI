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
			(0,200,255),
			(255,100,0),
			(255,255,0),
			(255,0,0),
			(0,0,255),
			(155,0,255)
		]
		colors_name = [
			'pink',
			'green',
			'blue',
			'orange',
			'yellow',
			'red',
			'dark blue',
			'violet'
		]
		self.name = colors_name[i]
		self.img = pygame.image.load('car'+str(i)+'.png')	
		self.img = pygame.transform.scale(self.img,(self.img.get_width()//20,self.img.get_height()//20))
		self.rot_img = self.img
		self.width = self.img.get_width()
		self.height = self.img.get_height()
		self.angle = 0
		self.speed = 5
		self.pos = [700,600]
		self.center = [self.pos[0]+self.width//2,self.pos[1]+self.height//2]
		self.radars = []
		self.is_alive = True
		self.dist = 0
		self.score = 0
		self.color_radar = colors_radar[i]
		self.clock = pygame.time.Clock()
		self.time = 0.1

	def timer(self):
		self.clock.tick()
		self.time += self.clock.get_rawtime()

	def rotate_img(self):
		self.rot_img = pygame.transform.rotate(self.img,self.angle)

	def check_collision(self):
		lw = self.width
		lh = self.height
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
			if not(1<dot[0]<road_width) or not(1<dot[1]<road_height) or road.get_at((dot[0],dot[1])) == (180,255,115,255):
				self.is_alive = False

	def check_radars(self):
		self.radars = []
		for degree in [-150,-120,-60,-30,0,30,60,120,150]:
			length = 0
			while length < 300:
				x = self.center[0] + int(length*math.cos(math.radians(degree-self.angle)))
				y = self.center[1] + int(length*math.sin(math.radians(degree-self.angle)))
				if not(1<x<road_width) or not(1<y<road_height) or road.get_at((x,y)) == (180,255,115,255):
					break
				length += 1
			self.radars.append([(x,y),length])
	
	def drive(self):
		self.pos[0] += int(self.speed*math.cos(math.radians(360 - self.angle)))
		self.pos[1] += int(self.speed*math.sin(math.radians(360 - self.angle)))
		self.center = [self.pos[0]+self.width//2,self.pos[1]+self.height//2]
		self.dist += self.speed

	def draw_car(self,win):
		win.blit(self.rot_img,(self.center[0]-self.rot_img.get_width()//2,self.center[1]-self.rot_img.get_height()//2))

	def draw_radars(self,win):
		for radar in self.radars:
			pygame.draw.line(win,self.color_radar,self.center,radar[0],2)
			pygame.draw.circle(win,self.color_radar,radar[0],4)

	def get_data(self):
		ret = [0,0,0,0,0,0,0,0,0]
		for i in range(len(self.radars)):
			ret[i] = self.radars[i][1]//30
		
		return ret

	def get_score(self):
		self.score = self.dist*int(self.dist/(self.time/100))
	
	def turn(self,i,nets,cars):
		n = nets[i].activate(self.get_data())
		a = n.index(max(n[:2]))
		if a == 0:
			self.angle += 2
		elif a == 1:
			self.angle -= 2
		# if max(car.score for car in cars) > 3000:
		a = n.index(max(n[3:]))
		if a == 3 and self.speed < 15:
			self.speed += 1
		elif a == 4 and self.speed > 3:
			self.speed -= 1

def text(win,text,width,height,size,font = 'Comic Sans MS',color = (0, 0, 0),bg_color = (80,80,80),bg = False,center = True):
	font = pygame.font.SysFont(font, size)
	text = font.render(text, True, color, bg_color) if bg else font.render(text, True, color)
	text_rect = text.get_rect()
	if center == True:
		text_rect.center = (width, height)
	else:
		text_rect.midleft = (width, height)
	win.blit(text, text_rect)

def print_text(win,generation,cars,best):
	text(win,'Generation : %d' % (generation), road_width - 200, 100, 50)
	text(win,'Cars : %d' % (cars), 220, road_height - 100, 30)
	text(win,'Best score : %d' % (best), 220, road_height - 50, 30)
	text(win,'Press TAB for check info', road_width - 90, road_height - 30, 10)
	text(win,'Press SHIFT for show radars', road_width - 90, road_height - 20, 10)
	text(win,'Press SPACE for change generation', road_width - 90, road_height - 10, 10)	

def print_tab(win,generation,alive_cars,cars):
	# win.fill([50,50,50])
	# text(win,'Generation : %d' % (generation), road_width//2, 40, 70)
	# text(win,'Cars : %d' % (alive_cars), road_width//2, 100, 40)

	font = pygame.font.SysFont('Comic Sans MS', 40)
	for i,car in enumerate(filter(lambda x: x.is_alive, cars)):	
		color = car.color_radar if car.is_alive else (10,10,10)
		bg_color = (80,80,80) if car.is_alive else (50,50,50)
		text(win,'Color : %-40s' % (car.name), 10, 140 + 40*i, 20, color=color, bg_color=bg_color, bg=True, center=False)
		text(win,'Distance : %-20d' % (car.dist), 180, 140 + 40*i, 20, color=color, bg_color=bg_color, bg=True, center=False)
		# text(win,'Time : %02d:%02d:%02d%7s' % (car.time//60000,(car.time//1000)%60,car.time%60%100000,''), 350, 140 + 40*i, 20, color=color, bg_color=bg_color, bg=True, center=False)
		text(win,'Score : %-2d' % (car.score), 350, 140 + 40*i, 20, color=color, bg_color=bg_color, bg=True, center=False)



def start(genomes,config):
	cars = []
	nets = []
	global generation
	generation += 1
	global best_score
	global show_radars
	global check_tab

	for i, g in genomes:
		net = neat.nn.FeedForwardNetwork.create(g, config)
		nets.append(net)
		g.fitness = 0

		cars.append(Car(i%8))

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
				car.timer()
				car.drive()
				car.check_radars()				
				car.turn(i,nets,cars)
				car.rotate_img()
				car.check_collision()
				car.draw_car(win)
				car.get_score()
				if show_radars: car.draw_radars(win)
				genomes[i][1].fitness += car.score

		for event in pygame.event.get():
			keys = pygame.key.get_pressed()
			if event.type == pygame.QUIT:
				sys.exit()			
			if event.type == pygame.KEYDOWN:
				if keys[pygame.K_SPACE]:
					run = False
				if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
					show_radars = not(show_radars)
				if keys[pygame.K_TAB]:
					check_tab = not(check_tab)

		print_text(win,generation,alive_cars,best_score)		
		
		if alive_cars == 0 or max(car.dist for car in cars) > 9000:
			run = False

		for i in range(len(trees)):
			win.blit(trees[i],tree_coords[i])

		if check_tab: print_tab(win,generation,alive_cars,cars)
		
		pygame.display.update()	
			

pygame.init()
road = pygame.image.load('road.png')
road = pygame.transform.scale(road,(road.get_width()//3*2,road.get_height()//3*2))
road_width = road.get_width()
road_height = road.get_height()
win = pygame.display.set_mode((road_width,road_height))
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
show_radars = False
check_tab = False

config_path = "./config-feedforward.txt"
config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

p = neat.Population(config)

p.add_reporter(neat.StdOutReporter(True))
stats = neat.StatisticsReporter()
p.add_reporter(stats)

p.run(start, 1000)
# while True:
# 	for event in pygame.event.get():
# 		if event.type == pygame.QUIT:
# 			sys.exit()
# 		if event.type == pygame.KEYDOWN:
# 			p.run(start, 1000)