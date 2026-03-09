import pygame, sys, subprocess, random
pygame.init()

window = pygame.display.set_mode((600,750))

x= 65
y= 50
width = 450
height = 600

run = True
while run:
    pygame.time.delay(100)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            command = "main.py"
            subprocess.call(command)
            
    window.fill((255,255,255))
    pygame.draw.rect(window, (0,0,0), (x,y,width,height))
    pygame.display.update()
pygame.quit()
sys.exit(0)