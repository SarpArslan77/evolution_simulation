import pygame
import sys

# Initialize Pygame
pygame.init()

# Set up display
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Basic Display")
clock = pygame.time.Clock()

# Set up colors
white = [255, 255, 255]
gray = [75, 90, 100]
yellow = [230, 250, 30]
bright_blue = [190, 250, 250]

hazel = [250, 125, 75]
blue = [30, 15, 120]
dark_blue = [10, 15, 70]
orange = [250, 180, 80]

loop: int = 1
sky_color = bright_blue[:]
sun_color = yellow[:]
moon_color = gray[:]

# Main game loop
running = True
while running:
     # Handle events
     for event in pygame.event.get():
          if event.type == pygame.QUIT:
               running = False

    # Fill the screen with white
     loop += 1
    
     if 0 < loop <= 500 : # sun staying
          # bright_blue sky
          screen.fill((round(sky_color[0]), round(sky_color[1]), round(sky_color[2])))
          # yellow sun
          pygame.draw.rect(screen, (round(sun_color[0]), round(sun_color[1]), round(sun_color[2])), (350, 250, 100, 100))
     elif 500 < loop <= 1000: # sun going down
          # orange sky
          screen.fill((round(sky_color[0]), round(sky_color[1]), round(sky_color[2])))
          sky_color[0] += (orange[0]-sky_color[0])/500
          sky_color[1] += (orange[1]-sky_color[1])/500
          sky_color[2] += (orange[2]-sky_color[2])/500
          # hazel sun
          pygame.draw.rect(screen, (round(sun_color[0]), round(sun_color[1]), round(sun_color[2])), (350, loop-250, 100, 100))
          sun_color[0] += (hazel[0]-sun_color[0])/500
          sun_color[1] += (hazel[1]-sun_color[1])/500
          sun_color[2] += (hazel[2]-sun_color[2])/500
     elif 1000 < loop <= 1500: # transition from sun to moon
          # blue sky
          screen.fill((round(sky_color[0]), round(sky_color[1]), round(sky_color[2])))
          sky_color[0] += (blue[0]-sky_color[0])/500
          sky_color[1] += (blue[1]-sky_color[1])/500
          sky_color[2] += (blue[2]-sky_color[2])/500
     elif 1500 < loop <= 2000: # moon rising
          # dark blue sky
          screen.fill((round(sky_color[0]), round(sky_color[1]), round(sky_color[2])))
          sky_color[0] += (dark_blue[0]-sky_color[0])/500
          sky_color[1] += (dark_blue[1]-sky_color[1])/500
          sky_color[2] += (dark_blue[2]-sky_color[2])/500
          # gray moon
          pygame.draw.rect(screen, (round(moon_color[0]), round(moon_color[1]), round(moon_color[2])), (350, 2250-loop, 100, 100))
          moon_color[0] += (white[0]-moon_color[0])/500
          moon_color[1] += (white[1]-moon_color[1])/500
          moon_color[2] += (white[2]-moon_color[2])/500
     elif 2000 < loop <= 2500: # moon staying
          # dark blue sky
          screen.fill((round(sky_color[0]), round(sky_color[1]), round(sky_color[2])))
          # white moon
          pygame.draw.rect(screen, (round(moon_color[0]), round(moon_color[1]), round(moon_color[2])), (350, 250, 100, 100))
     elif 2500 < loop <= 3000: # moon going down
          # blue sky
          screen.fill((round(sky_color[0]), round(sky_color[1]), round(sky_color[2])))
          sky_color[0] += (blue[0]-sky_color[0])/500
          sky_color[1] += (blue[1]-sky_color[1])/500
          sky_color[2] += (blue[2]-sky_color[2])/500
          # gray moon
          pygame.draw.rect(screen, (round(moon_color[0]), round(moon_color[1]), round(moon_color[2])), (350, loop-2250, 100, 100))
          moon_color[0] += (gray[0]-moon_color[0])/500
          moon_color[1] += (gray[1]-moon_color[1])/500
          moon_color[2] += (gray[2]-moon_color[2])/500
     elif 3000 < loop <= 3500: # transition from moon to sun
          # blue sky
          screen.fill((round(sky_color[0]), round(sky_color[1]), round(sky_color[2])))
     elif 3500 < loop <= 4000: # sun going up
          # bright blue sky
          screen.fill((round(sky_color[0]), round(sky_color[1]), round(sky_color[2])))
          sky_color[0] += (bright_blue[0]-sky_color[0])/500
          sky_color[1] += (bright_blue[1]-sky_color[1])/500
          sky_color[2] += (bright_blue[2]-sky_color[2])/500
          # yellow sun
          pygame.draw.rect(screen, (round(sun_color[0]), round(sun_color[1]), round(sun_color[2])), (350, 4250-loop, 100, 100))
          sun_color[0] += (white[0]-sun_color[0])/500
          sun_color[1] += (white[1]-sun_color[1])/500
          sun_color[2] += (white[2]-sun_color[2])/500
     elif 4000 < loop: # reset the loop
          loop %= 4000

     # Update the display
     pygame.display.update()
     clock.tick(100)

# Quit Pygame
pygame.quit()
sys.exit()
