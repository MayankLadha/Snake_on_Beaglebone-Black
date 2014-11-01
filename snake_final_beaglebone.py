import pygame							# for graphics
import random							# to generate random integer
import sys								# system specific parameters and functions
import os								# to use fork
import subprocess						# to create a subprocess
import Adafruit_BBIO.GPIO as GPIO		# for BBB GPIO pins
import time								# for wait
from pygame.locals import *

# to check if the snake has collided with wall, apple or itself
def collide(x1, x2, y1, y2, w1, w2, h1, h2):
	if x1+w1 > x2 and x1 < x2+w2 and y1+h1 > y2 and y1 < y2+h2:
		return True
	else:
		return False

# actions to take if the snake has died and the game has finished
def die(screen, score):
	f = pygame.font.SysFont('Chiller', 70)
	t = f.render('Game Over!!!', True, (255, 255, 255))
	t1 = f.render('Your score: '+str(score), True, (255, 255, 255))
	screen.blit(t, (150, 200))
	screen.blit(t1, (135, 270))

	f = pygame.font.SysFont('Chiller', 25)
	t = f.render('Hit "ANY" key to Play Again!', True, (255, 255, 255))
	screen.blit(t, (170, 350))

	# file handling so that the high score can be maintained even if the program has started again
	fo = open("high_score.txt", "r")
	hs = fo.read(3)
	fo.close()
	if score > int(hs):
		fo = open("high_score.txt", "w")
		fo.write(str(score))
		fo.close()

		fo = open("high_score.txt", "r")
		hs = fo.read(4)
		fo.close()

		blackbox = pygame.Surface((40, 20))
		blackbox.fill((0, 0, 0))
		screen.blit(blackbox, (560, 10))

		f = pygame.font.SysFont('Chiller', 20)
		t = f.render('High score: '+str(hs), True, (255, 255, 255))
		screen.blit(t, (490, 10))

		f = pygame.font.SysFont('Chiller', 35)
		t = f.render('Congrats!!!', True, (255, 255, 255))
		screen.blit(t, (220, 70))

		f = pygame.font.SysFont('Chiller', 35)
		t = f.render('You have a new High score...', True, (255, 255, 255))
		screen.blit(t, (140, 100))

		# to fork a process and parallely run the sound effect
		if os.fork() == 0:
			print subprocess.call('ffmpeg -i applause.wav  -f alsa "default:CARD=Device" -re -vol 250', shell=True)
			os._exit(0)
	else:
		if os.fork() == 0:
			print subprocess.call('ffmpeg -i game_over.wav  -f alsa "default:CARD=Device" -re -vol 250', shell=True)
			os._exit(0)

	pygame.time.wait(2000) 
	pygame.display.update()
	while True:
		s1_state = GPIO.input("P9_13") 		# move up
		s2_state = GPIO.input("P9_11") 		# move left
		s3_state = GPIO.input("P9_15") 		# move down
		s4_state = GPIO.input("P9_21") 		# move right
		
		# to quit the game if the window is closed
		for e in pygame.event.get():
			if e.type == QUIT:
				pygame.quit()
				sys.exit(0)
		
		# to execute “Hit any key to play again” facility
		if s1_state == 1 or s2_state == 1 or s3_state == 1 or s4_state == 1:
			play_again();

# code to be executed when a player completes his level and moves on to the next level
def levelComplete(screen, score):
	blackbox = pygame.Surface((40, 20))
	blackbox.fill((0, 0, 0))
	screen.blit(blackbox, (300, 10))

	f = pygame.font.SysFont('Chiller', 20)
	t = f.render('Level '+str(level)+'                                                     Score: '+str(score), True, (255, 255, 255))
	screen.blit(t, (10, 10))

	f = pygame.font.SysFont('Chiller', 70)
	t = f.render('Level '+str(level)+' Complete!!!', True, (255, 255, 255))
	screen.blit(t, (100, 130))
	t1 = f.render('Your score: '+str(score), True, (255, 255, 255))
	screen.blit(t1, (150, 270))

	# to fork a process and parallely run the sound effect
	if os.fork() == 0:
		print subprocess.call('ffmpeg -i applause.wav  -f alsa "default:CARD=Device" -re -vol 250', shell=True)
		os._exit(0)
	
	pygame.display.update()
	pygame.time.wait(3000)

# the actual playing method
def play_again():
	# all the declarations and initializations
	xs = [290, 290, 290, 290, 290]
	ys = [290, 270, 250, 230, 210]
	dirs = 0
	score = 0
	global level
	level = 1
	prevLevelScore = 0
	applepos = (random.randint(0, 590), random.randint(0, 590))
	pygame.init()
	s = pygame.display.set_mode((600, 600))
	pygame.display.set_caption('Snake')
	appleimage = pygame.image.load('apple.bmp')
	appleimage = pygame.transform.scale(appleimage, (20, 15))
	img = pygame.Surface((15, 15))
	img.fill((255, 0, 0))
	img1 = pygame.Surface((20, 20))
	img1.fill((0, 0, 200))
	f = pygame.font.SysFont('Chiller', 20)
	clock = pygame.time.Clock()
	
	# the infinite loop to actually make the snake move
	while True:	
		clock.tick(9+level)
		for e in pygame.event.get():
			if e.type == QUIT:
				pygame.quit()
				sys.exit(0)

		s1_state = GPIO.input("P9_13") 		# move up
		s2_state = GPIO.input("P9_11") 		# move left
		s3_state = GPIO.input("P9_15") 		# move down
		s4_state = GPIO.input("P9_21") 		# move right
		print "up: " + str(s1_state)
		print "left: " + str(s2_state)
		print "down: " + str(s3_state)
		print "right: " + str(s4_state)
				
		# change the direction of the snake when the respective key is pressed
		if s1_state == 1 and dirs != 0:			# move up
			dirs = 2
		elif s3_state == 1 and dirs != 2:			# move down
			dirs = 0
		elif s2_state == 1 and dirs != 1:			# move left
			dirs = 3
		elif s4_state == 1 and dirs != 3:			# move right
			dirs = 1

		i = len(xs)-1
		while i >= 2:
			# if the snake collides with itself
			if collide(xs[0], xs[i], ys[0], ys[i], 20, 20, 20, 20):
				die(s, score)
			i-= 1

		# if the snake collides with the apple OR if the snake eats the apple	
		if collide(xs[0], applepos[0], ys[0], applepos[1], 20, 10, 20, 10):
			score += 10;

			# to fork a process and parallely run the sound effect
			if os.fork() == 0:
				print subprocess.call('ffmpeg -i eat.wav  -f alsa "default:CARD=Device" -re -vol 250', shell=True)
				os._exit(0)

			xs.append(700)
			ys.append(700)
			if score >= prevLevelScore+30:
				prevLevelScore = score
				levelComplete(s, score)
				level = level+1

			# randomly generate apple’s position
			applepos = (random.randint(0,590),random.randint(0,590))
			
		# if the snake collides with the wall
		if xs[0] < 0 or xs[0] > 580 or ys[0] < 0 or ys[0] > 580:
			die(s, score)
			
		i = len(xs)-1
		
		while i >= 1:
			xs[i] = xs[i-1];
			ys[i] = ys[i-1];
			i -= 1
			
		# to update the respective xs and ys values
		if dirs == 0:				# move down
			ys[0] += 20
		elif dirs == 1:				# move right
			xs[0] += 20
		elif dirs == 2:
			ys[0] -= 20			# move up
		elif dirs == 3:
			xs[0] -= 20			# move left
			
		# background color of the window
		s.fill((0, 0, 0))
		
		# display the snake
		for i in range(0, len(xs)):
			s.blit(img, (xs[i], ys[i]))
			
		# display the apple
		s.blit(appleimage, applepos)

		# show the score and high score on the top of the window
		t=f.render('Level '+str(level)+'                                                     Score: '+str(score), True, (255, 255, 255))
		s.blit(t, (10, 10))

		fo = open("high_score.txt", "r")
		hs = fo.read(3)
		fo.close()

		f = pygame.font.SysFont('Chiller', 20)
		t = f.render('High score: '+str(hs), True, (255, 255, 255))
		s.blit(t, (490, 10))
		
		# update the display
		pygame.display.update()

# main function: program execution starts from here
# initialization of the BBB GPIO pins
GPIO.setup("P9_13", GPIO.IN)
GPIO.setup("P9_11", GPIO.IN)
GPIO.setup("P9_15", GPIO.IN)
GPIO.setup("P9_21", GPIO.IN)
s1_state = GPIO.input("P9_13")
s2_state = GPIO.input("P9_11")
s3_state = GPIO.input("P9_15")
s4_state = GPIO.input("P9_21")

# start the game
play_again();
