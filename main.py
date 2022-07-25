import sys
import pygame
from pygame.locals import *

from renderer import Renderer
from director import Director

pygame.init()

SHOT = False

FPS = 60
fpsClock = pygame.time.Clock()

width, height = 1280, 720
screen = pygame.display.set_mode((width, height))

director = Director(width, height)
renderer = Renderer(screen, width, height, director)

last_pressed = 0
last_esc = 0


def process_inputs():
    global last_pressed
    global last_esc

    mouse_pressed = pygame.mouse.get_pressed()
    # Shoot projectile
    if not director.paused and director.started:
        global SHOT
        if not director.player.shield:
            if mouse_pressed[0] and not SHOT:
                director.shoot(pygame.mouse.get_pos())
                SHOT = True
            if not mouse_pressed[0]:
                SHOT = False
    else:
        if mouse_pressed[0]:
            if director.selected_menu == 1:
                if not director.started:
                    director.started = True
                    director.start_game()
                director.paused = False
            elif director.selected_menu == 2 and pygame.time.get_ticks() - last_esc > 100:

                director.show_controls = True
            elif director.selected_menu == 3 and pygame.time.get_ticks() - last_esc > 100:
                if not director.started and not director.show_controls:
                    exit()
                elif director.paused and not director.show_controls:
                    director.paused = False
                    director.started = False
                else:
                    director.show_controls = False
            last_esc = pygame.time.get_ticks()

    # Process keyboard input
    pressed = pygame.key.get_pressed()
    if pressed[K_ESCAPE]:
        # Change game state
        if pygame.time.get_ticks() - last_esc > 100:
            if not director.started:
                exit()
            elif director.dead:
                director.dead = False
                director.started = False
                last_esc = pygame.time.get_ticks()
            director.paused = not director.paused
            last_esc = pygame.time.get_ticks()
    if director.paused or not director.started:
        return
    if pressed[K_LEFT] or pressed[K_a]:
        director.move(0)
    elif pressed[K_RIGHT] or pressed[K_d]:
        director.move(1)
    else:
        director.player.speed = 0
    if pressed[K_SPACE] or pressed[K_UP]:
        if (pygame.time.get_ticks() - last_pressed) > 200:
            director.move(2)
            last_pressed = pygame.time.get_ticks()
    if pressed[K_F5]:
        director.debug = not director.debug
        if director.debug:
            print("DEBUG MODE ON")
        else:
            print("DEBUG MODE FF")
    if pressed[K_LSHIFT]:
        director.player.shield = True
    else:
        director.player.shield = False
    if pressed[K_e] and director.player.interactible:
        if (pygame.time.get_ticks() - last_pressed) > 1000:
            director.player.interacted = True
            last_pressed = pygame.time.get_ticks()

    # Process mouse input




def main():
    # Game loop
    while True:
        if not director.started or director.paused:
            pygame.mouse.set_visible(True)
        else:
            pygame.mouse.set_visible(False)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        process_inputs()
        director.update()
        renderer.render_game(pygame.mouse.get_pos())

        pygame.display.update()
        fpsClock.tick(60)


if __name__ == '__main__':
    main()
    print('PyCharm')
