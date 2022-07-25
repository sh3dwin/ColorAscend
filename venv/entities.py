import pygame
import random

# Define player calss here

class Player:

    playerHeight = 55
    playerWidth = 30

    rightFoot = 0

    items = []
    balance = 10000

    # State will be used to render the type of action the character is in
    # 0 for standing still
    # 1 for running
    # 2 for jumping
    state = 0

    # The position of the player
    positionX = 0
    positionY = 0

    # Whether the shiled is active or not
    shield = False

    # The jumping power of the player
    jumpPower = 0
    jumpCount = 0
    jumping = False

    position = 0

    # Which direction the player is facing
    # 0 for left
    # 1 for right
    direction = 0

    # Used to see if the player is next to an interactible
    interactible = False
    interacted = False

    def __init__(self, X, Y):
        self.positionY = Y - self.playerHeight
        self.positionX = X
        # Defines the starting health of the player
        self.health = 10
        # Defines the starting speed of the player
        self.speed = 0
        # Defubes the maximum speed of the player
        self.max_speed = 5
        # Defines the starting attack power of the player
        self.attack = 1
        # Defines the number of extra projectiles the player shoots at the start
        self.burst = 1
        # Defines the number of jumps the player has at the start
        self.jump = 1

    def add_item(self, item):
        self.items.append(item)

# Define projectile class here
class Projectile:
    size = 5
    speed = 10
    color = 0
    positionX = 0
    positionY = 0

    dirX = 0
    dirY = 0

    # if color is 3 then its an enemies projectile

    # Keeps track of the number of bounces
    bounce = 0

    def __init__(self, posX, posY, dirX, dirY, color):
        self.positionY = posY
        self.positionX = posX

        self.dirY = dirY
        self.dirX = dirX

        self.color = color


class Item:
    taken = 0

    positionX = 0
    positionY = 0

    timer = 0

    type = 0

    def __init__(self, posX, posY, type):
        """
        Creates an item entity of certain type.

        :param type: Integer resembling item type (1 - Speed-up, 2 - Extra jump, 3 - More projectiles, 4 - Attack power increase)
        """
        self.positionY = posY
        self.positionX = posX
        self.type = type

    def __str__(self):
        if self.type == 1:
            return "Speed-up"
        if self.type == 2:
            return "Extra jump"
        if self.type == 3:
            return "More projectiles"
        if self.type == 4:
            return "More attack power"
        if self.type == 5:
            return "Coin"
        if self.type == 6:
            return "Bomb"
        if self.type == 7:
            return "Chest"
        else:
            return "Error".join(str(type))

# Define enemy class ehre

class Enemy:
    health = 0
    attack_power = 0
    speed = 0
    xpos = 0
    ypos = 0
    timer = 0

    alive = False

    def __init__(self, xpos, ypos, health, attack_power, speed):
        """
            Creates an enemy with the given parameters.

        :param xpos:
        :param ypos:
        :param health:
        :param attack_power:
        :param speed:
        """
        # 1 for red, 2 for green, 3 for blue
        self.xpos = xpos
        self.ypos = ypos
        self.color = random.randint(0, 2)
        self.health = health
        self.attack_power = attack_power
        self.speed = speed
        self.alive = True
        self.timer = random.randint(0, 200)


# Define blob class here

class Blob(Enemy):

    # -1 - left, 1 - right
    direction = 0

    # cost of blob
    cost = 1

    width = 40
    height = 40

    # helper variable for jumping animation

    def __init__(self, xpos, ypos):
        super().__init__(xpos, ypos, 5, 1, 5)
        self.direction = -1

    def hit(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.alive = False


# Define bomber class here
# drops a bomb a level below that has a delayed explosion and does splash damage

class Bomber(Enemy):
    # cost of blob
    cost = 3
    width = 100
    height = 100

    # helper variable for jumping animation

    def __init__(self, xpos, ypos):
        super().__init__(xpos, ypos, 15, 1, 5)
        self.direction = -1

    def hit(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.alive = False

# Define painter class here
# paints a tile black for a certain duration

# Define color lord class here