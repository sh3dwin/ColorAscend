# Render the back texture first, then render the level, then render the menu
# Back texture should be dirt or something with the edges of the level being walls
# Bottom edge of level should be grass while top should stay open until end is visible

import pygame
import math
from director import Director, checkRectangleCollisions
import entities
import copy


class Renderer():

    # Keeps track of the game state
    # 0 for starting menu
    # 1 for playing
    # 2 for transition
    # 3 for game failed
    game_state = 1
    last_offset = 0
    counter = 0
    last_item = None
    start_counter = 0
    death_counter = 0

    def __init__(self, screen, screen_width, screen_height, director):
        self.director = director
        self.screen = screen
        self.game_state = 1
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Load resources ===============================================================================================

        # Load general resources
        self.dirt_image = pygame.image.load("dirt.jpg")
        self.grass_image = pygame.image.load("grass.jpg")
        self.lv1_background = pygame.image.load("new_background.png")
        self.door = pygame.image.load("door.png")
        self.door = pygame.transform.scale(self.door, (70, 100))

        # Load character resources
        self.character_legs_1 = pygame.image.load("legs_1.PNG")
        self.character_legs_2 = pygame.image.load("legs_2.PNG")
        self.character_head = pygame.image.load("head.PNG")
        self.character_body = pygame.image.load("body.PNG")
        self.character_gun = pygame.image.load("gun.PNG")
        self.bubble = pygame.image.load("bubble.png")
        self.bubble = pygame.transform.scale(self.bubble, (80, 80))


        # Load item resources
        self.lv1_background = pygame.transform.scale(self.lv1_background, (self.screen_width / 6 * 4 + 12, self.lv1_background.get_height()))
        self.heart = pygame.image.load("heart.png")
        self.heart = pygame.transform.scale(self.heart, (40, 40))
        self.jump_up = pygame.image.load("jump_up.png")
        self.jump_up = pygame.transform.scale(self.jump_up, (40, 40))
        self.speed_up = pygame.image.load("speed_up.png")
        self.speed_up = pygame.transform.scale(self.speed_up, (40, 40))
        self.burst_up = pygame.image.load("burst_up.png")
        self.burst_up = pygame.transform.scale(self.burst_up, (40, 40))
        self.attack_up = pygame.image.load("attack_up.png")
        self.attack_up = pygame.transform.scale(self.attack_up, (40, 40))
        self.bomb = pygame.image.load("bomb.png")
        self.bomb = pygame.transform.scale(self.bomb, (40, 40))
        self.chest = pygame.image.load("chest.png")
        self.chest = pygame.transform.scale(self.chest, (40, 40))
        self.opened_chest = pygame.image.load("opened_chest.png")
        self.opened_chest = pygame.transform.scale(self.opened_chest, (40, 40))

        # Load enemies resources
        self.blobg = pygame.image.load("blob_green.png")
        self.blobg = pygame.transform.scale(self.blobg, (40, 40))
        self.blobr = pygame.image.load("blob_red.png")
        self.blobr = pygame.transform.scale(self.blobr, (40, 40))
        self.blobb = pygame.image.load("blob_blue.png")
        self.blobb = pygame.transform.scale(self.blobb, (40, 40))

        self.bomberR = pygame.image.load("bomber_red.png")
        self.bomberR = pygame.transform.scale(self.bomberR, (100, 100))
        self.bomberG = pygame.image.load("bomber_green.png")
        self.bomberG = pygame.transform.scale(self.bomberG, (100, 100))
        self.bomberB = pygame.image.load("bomber_blue.png")
        self.bomberB = pygame.transform.scale(self.bomberB, (100, 100))

        self.bomberR_g = pygame.image.load("bomber_red_grab.png")
        self.bomberR_g = pygame.transform.scale(self.bomberR_g, (100, 100))
        self.bomberG_g = pygame.image.load("bomber_green_grab.png")
        self.bomberG_g = pygame.transform.scale(self.bomberG_g, (100, 100))
        self.bomberB_g = pygame.image.load("bomber_blue_grab.png")
        self.bomberB_g = pygame.transform.scale(self.bomberB_g, (100, 100))

        self.bomberR_d = pygame.image.load("bomber_red_drop.png")
        self.bomberR_d = pygame.transform.scale(self.bomberR_d, (100, 100))
        self.bomberG_d = pygame.image.load("bomber_green_drop.png")
        self.bomberG_d = pygame.transform.scale(self.bomberG_d, (100, 100))
        self.bomberB_d = pygame.image.load("bomber_blue_drop.png")
        self.bomberB_d = pygame.transform.scale(self.bomberB_d, (100, 100))


    def change_state(self, new_state):
        self.game_state = new_state

    def render_game(self, mouse_pos):
        if self.director.show_controls:
            self.darken_backgroun(255)
            self.render_controls(mouse_pos)
            return
        if not self.director.started:
            self.darken_backgroun(150)
            self.render_main_menu(mouse_pos)
            return
        self.render_level(mouse_pos)
        if self.director.transition:
            self.director.transition_counter += 1
            if self.director.transition_counter == 510:
                self.director.transition_counter = 0
                self.director.transition = False
            if self.director.transition_counter == 255:
                self.director.next_level()
                self.start_counter = 0
            if not self.director.transition_counter > 255:
                self.darken_backgroun(self.director.transition_counter)
            else:
                self.darken_backgroun(510 - self.director.transition_counter)
        if self.director.dead:
            self.darken_backgroun(155)
            self.render_death()
            return
        if self.start_counter < 500:
            self.start_counter += 1
            self.render_level_info()
        if self.director.paused:
            self.darken_backgroun(150)
            self.render_menu(mouse_pos)

    def render_death(self):
        text4 = self.get_text_rect(0, 0, "Game Over", 100)
        text4_rect = text4.get_rect(center=(self.screen_width / 2, (self.screen_height / 6 * 2)))
        self.screen.blit(text4, text4_rect)
        string = "Score " + str(self.director.score)
        text5 = self.get_text_rect(0, 0, string, 100)
        text5_rect = text5.get_rect(center=(self.screen_width / 2, (self.screen_height / 6 * 3)))
        self.screen.blit(text5, text5_rect)

    def render_level_info(self):
        string = "Level " + str(self.director.level)
        if self.start_counter < 255:
            alpha = 255
        alpha = (500 - self.start_counter) if 500 - self.start_counter > 0 else 0
        if self.director.debug and (alpha == 510 or alpha == 1):
            print("start_text::alpha: ", alpha)
        self.render_text_alpha(self.screen_width / 2 - 70, self.screen_height - 60, string, 70, alpha)

    def render_controls(self, mouse_pos):
        text1 = self.get_text_rect(0, 0, "A / D or <- / -> - Move left / Move Right", 50)
        text1_rect = text1.get_rect(center=(self.screen_width / 4, (self.screen_height / 6 * 2)))
        self.screen.blit(text1, text1_rect)
        text2 = self.get_text_rect(0, 0, u"SPACE or UP_ARROW - Jump", 50)
        text2_rect = text2.get_rect(center=(self.screen_width / 4 * 3, (self.screen_height / 6 * 2)))
        self.screen.blit(text2, text2_rect)
        text3 = self.get_text_rect(0, 0, "E - Interact", 50)
        text3_rect = text3.get_rect(center=(self.screen_width / 4 * 3, (self.screen_height / 6 * 3)))
        self.screen.blit(text3, text3_rect)
        text4 = self.get_text_rect(0, 0, "ESC - Pause or exit the game", 50)
        text4_rect = text4.get_rect(center=(self.screen_width / 4, (self.screen_height / 6 * 3)))
        self.screen.blit(text4, text4_rect)
        if mouse_pos[1] > (self.screen_height / 6 * 4 - 50) and mouse_pos[1] < (self.screen_height / 6 * 5 - 50):
            text5 = self.get_text_rect(0, 0, "Back", 120)
            self.director.selected_menu = 3
        else:
            text5 = self.get_text_rect(0, 0, "Back", 100)
            self.director.selected_menu = 3
        text5_rect = text5.get_rect(center=(self.screen_width / 2, (self.screen_height / 6 * 4)))
        self.screen.blit(text5, text5_rect)

    def darken_backgroun(self, alpha):
        bcg = pygame.Surface((self.screen_width, self.screen_height))
        bcg.fill((0, 0, 0))
        bcg.set_alpha(alpha)
        self.screen.blit(bcg, (0, 0))

    def render_cursor(self, mouse_pos):
        cursor_radius = 10
        pygame.draw.circle(self.screen, (255, 255, 255), mouse_pos, cursor_radius + 1, 3)
        pygame.draw.line(self.screen, (255, 255, 255), (mouse_pos[0] - cursor_radius, mouse_pos[1]), (mouse_pos[0] + cursor_radius - 1, mouse_pos[1]), 3)
        pygame.draw.line(self.screen, (255, 255, 255), (mouse_pos[0], mouse_pos[1] - cursor_radius), (mouse_pos[0], mouse_pos[1] + cursor_radius - 1), 3)

    def rotate(self, image, angle):
        """rotate an image while keeping its center and size"""
        orig_rect = image.get_rect()
        rot_image = pygame.transform.rotate(image, angle)
        rot_image.set_colorkey((0, 0, 0))
        rot_rect = orig_rect.copy()
        rot_rect.center = rot_image.get_rect().center
        center = rot_image.get_rect()
        return rot_image, center

    def render_player(self, mouse_pos):
        if self.director.dead:
            return
        # Render the player

        # Calculate the angle between cursor and player
        playerPosX = self.director.player.positionX
        playerPosY = self.director.player.positionY
        playerHeight = self.director.player.playerHeight
        playerWidth = self.director.player.playerWidth

        # angle = arctan(dy/dx)
        if (playerPosX - mouse_pos[0]) == 0:
            angle = 90
        else:
            angle = math.degrees(math.atan((playerPosY - mouse_pos[1])/(playerPosX - mouse_pos[0])))

        if mouse_pos[0] < self.director.player.positionX:
            self.director.player.direction = 0
        else:
            self.director.player.direction = 1

        if self.director.player.direction == 0:
            body = self.character_body
            body = pygame.transform.rotate(body, angle)
            head = self.character_head
            head = pygame.transform.rotate(head, angle)
            if self.director.player.rightFoot < 5:
                legs = self.character_legs_1
            else:
                legs = self.character_legs_2
            legs = pygame.transform.rotate(legs, angle)
            gun = self.character_gun
            gun = pygame.transform.rotate(gun, angle)
            self.screen.blit(pygame.transform.flip(body, True, False), (playerPosX, playerPosY))
            self.screen.blit(pygame.transform.flip(legs, True, False), (playerPosX, playerPosY))
            self.screen.blit(pygame.transform.flip(head, True, False), (playerPosX, playerPosY))
            self.screen.blit(pygame.transform.flip(gun, True, False), (playerPosX, playerPosY))
        else:

            body = self.character_body
            body = pygame.transform.rotate(body, -angle)
            head = self.character_head
            head = pygame.transform.rotate(head, -angle)
            if self.director.player.rightFoot < 5:
                legs = self.character_legs_1
            else:
                legs = self.character_legs_2
            legs = pygame.transform.rotate(legs, -angle)
            gun = self.character_gun
            gun = pygame.transform.rotate(gun, -angle)
            self.screen.blit(head, (playerPosX, playerPosY))
            self.screen.blit(body, (playerPosX, playerPosY))
            self.screen.blit(legs, (playerPosX, playerPosY))
            self.screen.blit(gun, (playerPosX, playerPosY))
        if self.director.player.shield:
            self.screen.blit(self.bubble, (playerPosX - 15, playerPosY - 10))



    def render_entities(self):
        offsetY = self.director.masterOffset
        # Render the entities
        for entity in self.director.getEntities():
            if isinstance(entity, entities.Projectile):
                if entity.color == 0:
                    color = (255, 0, 0)
                if entity.color == 1:
                    color = (0, 255, 0)
                if entity.color == 2:
                    color = (0, 0, 255)
                if entity.color == 3:
                    pygame.draw.circle(self.screen, (0, 0, 0), (entity.positionX, entity.positionY), entity.size * 1.2)
                    pygame.draw.circle(self.screen, (255, 255, 255), (entity.positionX, entity.positionY), entity.size, 2)
                    continue
                pygame.draw.circle(self.screen, color, (entity.positionX, entity.positionY), entity.size)
            elif isinstance(entity, entities.Blob):
                if self.director.debug:
                    pygame.draw.rect(self.screen, (255, 0, 0, 50), (entity.xpos, entity.ypos, entity.width, entity.height))
                if entity.color == 0:
                    self.screen.blit(self.blobr, (entity.xpos, entity.ypos))
                elif entity.color == 1:
                    self.screen.blit(self.blobg, (entity.xpos, entity.ypos))
                else:
                    self.screen.blit(self.blobb, (entity.xpos, entity.ypos))
            elif isinstance(entity, entities.Bomber):
                if self.director.debug:
                    pygame.draw.rect(self.screen, (255, 0, 0, 50), (entity.xpos, entity.ypos + 20, entity.width, entity.height - 20))
                if entity.timer < 400:
                    if entity.color == 0:
                        self.screen.blit(self.bomberR, (entity.xpos, entity.ypos))
                    if entity.color == 1:
                        self.screen.blit(self.bomberG, (entity.xpos, entity.ypos))
                    if entity.color == 2:
                        self.screen.blit(self.bomberB, (entity.xpos, entity.ypos))
                elif entity.timer < 450:
                    if entity.color == 0:
                        self.screen.blit(self.bomberR_g, (entity.xpos, entity.ypos))
                    if entity.color == 1:
                        self.screen.blit(self.bomberG_g, (entity.xpos, entity.ypos))
                    if entity.color == 2:
                        self.screen.blit(self.bomberB_g, (entity.xpos, entity.ypos))
                else:
                    if entity.color == 0:
                        self.screen.blit(self.bomberR_d, (entity.xpos, entity.ypos))
                    if entity.color == 1:
                        self.screen.blit(self.bomberG_d, (entity.xpos, entity.ypos))
                    if entity.color == 2:
                        self.screen.blit(self.bomberB_d, (entity.xpos, entity.ypos))
            elif isinstance(entity, entities.Item):
                if entity.type == 6:
                    self.render_item(entity)


    def render_background(self):
        for i in range(0, self.screen_width, 255):
            for j in range(0, self.screen_height, 132):
                self.screen.blit(self.dirt_image, (i, j))

    def render_sky(self):
        # Render the sky
        if self.director.masterOffset % 3 == 0 and self.director.masterOffset != self.last_offset:
            self.director.background_offset += 1
        self.last_offset = self.director.masterOffset
        # pygame.draw.rect(self.screen, (0, 150, 200), (self.screen_width / 6 - 6, 0, self.screen_width / 6 * 4 + 12, self.director.masterOffset))
        self.screen.blit(self.lv1_background, ((self.screen_width / 6), self.director.background_offset - 1760))

    def render_layout(self):
        # Render the layout
        layout = self.director.getLayout()
        offsetY = self.director.masterOffset
        index = 0
        interactible = False
        idx = 0
        for row in layout:
            offsetX = self.screen_width / 6
            tileWidth = ( (self.screen_width / 6) * 4 ) / 8
            pposx = self.director.player.positionX + self.director.player.playerWidth / 2
            pposy = self.director.player.positionY + self.director.player.playerHeight / 2
            # Render only visible rows, and one above that
            if offsetY > -200:
                for tile in row:
                    # Draw a tile if there is no gap
                    if tile != 0:
                        self.screen.blit(self.grass_image, (offsetX, offsetY))
                        # pygame.draw.rect(self.screen, (100, 0, 0), (offsetX, offsetY, tileWidth, 40))
                        if tile == 2:
                            item = self.director.getItems()[idx]
                            idx += 1
                            posx = offsetX + tileWidth/2
                            posy = offsetY - 60
                            item.positionX = offsetX + tileWidth/2
                            item.positionY = offsetY - 60 + 10 * math.cos(pygame.time.get_ticks() * 0.005)
                            if item.taken == 1:
                                self.screen.blit(self.opened_chest, (item.positionX, item.positionY))
                            else:
                                self.screen.blit(self.chest, (item.positionX, item.positionY))
                                inHoriz = pposx < posx + tileWidth / 2 and pposx > posx - tileWidth / 2
                                inVer = pposy < posy + 60 and pposy > posy
                                if inHoriz and inVer:
                                    interactible = True
                                    self.render_text(posx - 10, posy - 40, "[E] to open", 20)
                                    self.render_text(posx, posy - 15, str(self.director.level * 5), 20)
                                    self.render_spinning_coin(posx + 20, posy - 20, 10)
                    offsetX += tileWidth
            if index == len(layout) - 1:
                self.screen.blit(self.door, (self.screen_width / 2 - self.door.get_width() / 2 - 10, offsetY - self.door.get_height() + 15))
                if checkRectangleCollisions(self.director.player.positionX, self.director.player.positionY, self.director.player.playerWidth, self.director.player.playerHeight,
                                            self.screen_width / 2 - self.door.get_width() / 2 - 10, offsetY - self.door.get_height() + 15, self.door.get_width(), self.door.get_height()):
                    self.director.transition = True
                    return
            offsetY -= 150
            index += 1
            self.director.player.interactible = interactible


    def render_main_menu(self, mouse_pos):
        if mouse_pos[1] > (self.screen_height / 6 * 2 - 50) and mouse_pos[1] < (self.screen_height / 6 * 3 - 50):
            text1 = self.get_text_rect(0, 0, "Start game", 120)
            self.director.selected_menu = 1
        else:
            text1 = self.get_text_rect(0, 0, "Start game", 100)
        text1_rect = text1.get_rect(center=(self.screen_width / 2, (self.screen_height / 6 * 2)))
        self.screen.blit(text1, text1_rect)
        if mouse_pos[1] > (self.screen_height / 6 * 3 - 50) and mouse_pos[1] < (self.screen_height / 6 * 4 - 50):
            text2 = self.get_text_rect(0, 0, "Controls", 120)
            self.director.selected_menu = 2
        else:
            text2 = self.get_text_rect(0, 0, "Controls", 100)
        text2_rect = text2.get_rect(center=(self.screen_width / 2, (self.screen_height / 6 * 3)))
        self.screen.blit(text2, text2_rect)
        if mouse_pos[1] > (self.screen_height / 6 * 4 - 50) and mouse_pos[1] < (self.screen_height / 6 * 5 - 50):
            text3 = self.get_text_rect(0, 0, "Quit game", 120)
            self.director.selected_menu = 3
        else:
            text3 = self.get_text_rect(0, 0, "Quit game", 100)
        text3_rect = text3.get_rect(center=(self.screen_width / 2, (self.screen_height / 6 * 4)))
        self.screen.blit(text3, text3_rect)

    def render_menu(self, mouse_pos):
        if mouse_pos[1] > (self.screen_height / 6 * 2 - 50) and mouse_pos[1] < (self.screen_height/6 * 3 - 50):
            text1 = self.get_text_rect(0, 0, "Continue", 120)
            self.director.selected_menu = 1
        else:
            text1 = self.get_text_rect(0, 0, "Continue", 100)
        text1_rect = text1.get_rect(center=(self.screen_width/2, (self.screen_height/6 * 2)))
        self.screen.blit(text1, text1_rect)
        if mouse_pos[1] > (self.screen_height / 6 * 3 - 50) and mouse_pos[1] < (self.screen_height / 6 * 4 - 50):
            text2 = self.get_text_rect(0, 0, "Controls", 120)
            self.director.selected_menu = 2
        else:
            text2 = self.get_text_rect(0, 0, "Controls", 100)
        text2_rect = text2.get_rect(center=(self.screen_width / 2, (self.screen_height / 6 * 3)))
        self.screen.blit(text2, text2_rect)
        if mouse_pos[1] > (self.screen_height / 6 * 4 - 50) and mouse_pos[1] < (self.screen_height / 6 * 5 - 50):
            text3 = self.get_text_rect(0, 0, "Exit to main menu", 120)
            self.director.selected_menu = 3
        else:
            text3 = self.get_text_rect(0, 0, "Exit to main menu", 100)
        text3_rect = text3.get_rect(center=(self.screen_width / 2, (self.screen_height / 6 * 4)))
        self.screen.blit(text3, text3_rect)


    def render_level(self, mouse_pos):
        self.render_background()
        self.render_sky()
        self.render_layout()
        self.render_player(mouse_pos)
        self.render_entities()
        self.render_overlay()
        if not self.director.paused:
            self.render_cursor(mouse_pos)



    def render_transition(self):
        self.screen.fill((0, 0, 0))

    def render_death_screen(self):
        self.screen.fill((0, 0, 0))

    def render_spinning_coin(self, posX, posY, radius):
        newRadius = abs(math.cos(pygame.time.get_ticks() * 0.005)) * radius
        newPosX = posX + (radius - newRadius)
        pygame.draw.ellipse(self.screen, (255, 223, 0), (newPosX, posY, newRadius * 2, radius * 2))
        pygame.draw.ellipse(self.screen, (255, 200, 0), (newPosX, posY, newRadius * 2, radius * 2), width=int(radius/5))

    def render_text(self, posX, posY, text, fontSize):
        """
        Renders given text at a given location.

        :param posX: Horizontal position of the text
        :param posY: Vertical position of the text
        :param text: The text to be rendered
        :param fontSize: The size of the text
        :return:
        """
        pygame.font.init()
        font = pygame.font.SysFont('Kleyn', fontSize)
        text_surface = font.render(text, False, (255, 255, 255))
        self.screen.blit(text_surface, (posX, posY))

    def get_text_rect(self, posX, posY, text, fontSize):
        """
        Returns a text surface

        :param posX: Horizontal position of the text
        :param posY: Vertical position of the text
        :param text: The text to be rendered
        :param fontSize: The size of the text
        :return:
        """
        pygame.font.init()
        font = pygame.font.SysFont('Kleyn', fontSize)
        text_surface = font.render(text, False, (255, 255, 255))
        return text_surface

    def render_text_alpha(self, posX, posY, text, fontSize, alpha):
        """
        Renders given text at a given location.

        :param posX: Horizontal position of the text
        :param posY: Vertical position of the text
        :param text: The text to be rendered
        :param fontSize: The size of the text
        :return:
        """
        pygame.font.init()
        font = pygame.font.SysFont('Kleyn', fontSize)
        text_surface = font.render(text, False, (255, 255, 255))
        text_surface.set_alpha(alpha)
        self.screen.blit(text_surface, (posX, posY))

    def render_overlay(self):
        # Draw the coin amount the player has
        self.render_spinning_coin(20, 50, 20)
        self.render_text(75, 50, str(self.director.player.balance), 70)
        self.render_text(20, 150, "Score", 70)
        self.render_text(20, 250, str(self.director.score), 70)

        # Draw the health the player has
        offsetX = 0
        offsetY = 0
        health = self.director.player.health
        for i in range(health):
            self.screen.blit(self.heart, (10 + offsetX, 660 + offsetY))
            offsetX += 40
            if i % 5 == 4:
                offsetY -= 50 - 10 * int(health / 10)
                offsetX = 0

        # Draw the items the player has
        occured = []
        offsetX = self.screen_width / 6 * 5 + 20
        offsetY = 120
        self.render_text(1100, 50, "Items:", 70)
        for item in self.director.player.items:
            if not occured.__contains__(item.type):
                occured.append(item.type)
                if item.type == 1:
                    self.screen.blit(self.speed_up, (offsetX, offsetY))
                    text = "x"  +str(int((self.director.player.max_speed - 5)))
                    self.render_text(offsetX + 30, offsetY + 20, text, 30)
                if item.type == 2:
                    self.screen.blit(self.jump_up, (offsetX, offsetY))
                    text = "x" + str(int(self.director.player.jump - 1))
                    self.render_text(offsetX + 30, offsetY + 20, text, 30)
                if item.type == 3:
                    self.screen.blit(self.burst_up, (offsetX, offsetY))
                    text = "x" + str(int(self.director.player.burst - 1))
                    self.render_text(offsetX + 30, offsetY + 20, text, 30)
                if item.type == 4:
                    self.screen.blit(self.attack_up, (offsetX, offsetY))
                    text = "x" + str(int(self.director.player.attack - 1))
                    self.render_text(offsetX + 30, offsetY + 20, text, 30)
                if len(occured) % 3 == 0 and len(occured) != 0:
                    offsetX -= 120
                    offsetY += 60
                    continue
                offsetX += 60

        # Render the taken item message
        self.counter += 1
        if self.director.last_taken_item != None:
            if self.director.last_taken_item != self.last_item:
                if self.director.debug:
                    print("render_entities::last_item_taken: ", self.director.last_taken_item, " and ", self.last_item)
                self.counter = 0
                self.last_item = self.director.last_taken_item
            self.render_taken_item(self.director.last_taken_item)

    def render_item(self, item):
        if item.type == 1:
            self.screen.blit(self.speed_up, (item.positionX, item.positionY))
        elif item.type == 2:
            self.screen.blit(self.jump_up, (item.positionX, item.positionY))
        elif item.type == 3:
            self.screen.blit(self.burst_up, (item.positionX, item.positionY))
        elif item.type == 4:
            self.screen.blit(self.attack_up, (item.positionX, item.positionY))
        elif item.type == 5:
            self.render_coin_on_kill(item.posx, item.posy, 5)
        elif item.type == 6:
            self.screen.blit(self.bomb, (item.positionX, item.positionY))
            if item.timer < 66:
                self.render_text(item.positionX + 20, item.positionY + 20, "3", 20)
            elif item.timer < 133:
                self.render_text(item.positionX + 20, item.positionY + 20, "2", 20)
            else:
                self.render_text(item.positionX + 20, item.positionY + 20, "1", 20)

    def render_item_pos(self, type, positionX, positionY):
        if type == 1:
            self.screen.blit(self.speed_up, (positionX, positionY))
        if type == 2:
            self.screen.blit(self.jump_up, (positionX, positionY))
        if type == 3:
            self.screen.blit(self.burst_up, (positionX, positionY))
        if type == 4:
            self.screen.blit(self.attack_up, (positionX, positionY))

    def render_coin_on_kill(self, posx, posy, amount):
        self.counter += 1
        if self.counter > 100:
            self.counter = 0
            return
        self.render_spinning_coin(posx, posy - self.counter, 20)
        self.render_text(posx, posy - self.counter, str(amount), 70)

    def render_taken_item(self, item):
        string = str(item) + " received"
        if item.type == 1:
            it = copy.copy(self.speed_up)
        elif item.type == 2:
            it = copy.copy(self.jump_up)
        elif item.type == 3:
            it = copy.copy(self.burst_up)
        elif item.type == 4:
            it = copy.copy(self.attack_up)
        else:
            return

        if self.counter < 255:
            alpha = 255
        alpha = (510 - self.counter) if 510 - self.counter > 0 else 0
        it.set_alpha(alpha)
        if self.director.debug and (alpha == 510 or alpha == 1):
            print("render_taken_item::alpha: ",alpha)

        self.screen.blit(it, (self.screen_width/6 + 10, self.screen_height - 50))
        self.render_text_alpha(self.screen_width/6 + 70, self.screen_height - 40, string, 40, alpha)




