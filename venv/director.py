from entities import Player, Projectile, Item, Enemy, Blob, Bomber
import random
import pygame

class Director:
    # Holds every entity object
    entities = []
    last_taken_item = None
    # The current level
    level = 0
    # Holds the layout of a number of levels
    levels = []
    # Keeps track of the vertical position on the screen that the player should be located at when not jumping
    masterOffset = 0
    # Used to help with the transition when the player reaches the next row
    newMasterOffset = 0
    # Used to keep track of the background
    background_offset = 0
    # Used to help with the transition when the player reaches the next row
    baseY = 0
    # Used to keep track of bombers
    bombTimer = 0
    # Used to keep track of when the level switches
    switched = False
    debug = False
    paused = False
    started = False
    dead = False
    transition = False
    transition_counter = 0

    # Which menu item is selected 1 - Start/Continue, 2 - Controls, 3 - Exit/Back/Quit
    selected_menu = 0
    show_controls = False

    score = 0


    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height

    def start_game(self):
        self.levels = []
        self.player = None
        self.dead = False
        self.entities = []
        self.player = Player(self.screen_width/2, self.screen_height - 200)
        self.level = 1
        self.baseY = self.player.positionY + self.player.playerHeight
        self.masterOffset = self.player.positionY + self.player.playerHeight
        self.newMasterOffset = self.masterOffset
        self.background_offset = self.screen_height + 500
        self.switched = True
        self.levels.append(self.generateLayout())

    def next_level(self):
        self.player.positionY = self.screen_height - 200
        self.player.health += 10
        self.levels = []
        self.entities = []
        self.level += 1
        self.dead = False
        self.baseY = self.player.positionY + self.player.playerHeight
        self.masterOffset = self.player.positionY + self.player.playerHeight
        self.newMasterOffset = self.masterOffset
        self.background_offset = self.screen_height + 500
        self.switched = True
        self.levels.append(self.generateLayout())

    # Returns all entities in the game
    def getEntities(self):
        return self.entities

    def getItems(self):
        items = []
        for entity in self.entities:
            if isinstance(entity, Item) and entity.type != 6:
                items.append(entity)
        return items

    def getBombs(self):
        items = []
        for entity in self.entities:
            if isinstance(entity, Item) and entity.type == 6:
                items.append(entity)
        return items

    # Returns the player object
    def getPlayer(self):
        return self.player

    def getProjectiles(self):
        projectiles = []
        for entity in self.entities:
            if isinstance(entity, Projectile):
                projectiles.append(entity)
        return projectiles

    def getEnemies(self):
        enemies = []
        for entity in self.entities:
            if isinstance(entity, Enemy):
                enemies.append(entity)
        return enemies

    def getLayout(self):
        return self.levels[0]

    def generateLayout(self):
        # Level is stored as a list of rows
        layout = []
        for i in range(self.level * 5 + 5):
            # Find the gap in each row
            gap = -1
            if i != 0:
                gap = random.randrange(1, 8)
            row = []
            # Generate each row, each j is a different tile
            for j in range(8):
                if j == gap:
                    row.append(0)
                else:
                    row.append(1)
            if i % 5 == 4:
                item_pos = random.randint(0, 1)
                if gap == 0:
                    item_pos = 1
                elif gap == 7:
                    item_pos = 0

                if item_pos == 0:
                    row[0] = 2
                else:
                    row[7] = 2
                self.entities.append(Item(0, 0, 7))
            # Append each row to the level
            print(row)
            layout.append(row)
        exit = [0, 0, 0, 1, 1, 0, 0, 0]
        layout.append(exit)
        self.levels.append(layout)


    def move(self, action):
        """Moves the player acording to the action
        0 for moving left
        1 for moving right
        2 for jumping
        """
        if self.paused or self.dead or self.transition or not self.started:
            return
        if self.debug:
            print("move::player.rightFoot: ", self.player.rightFoot)
        if action == 0:
            self.player.rightFoot = (self.player.rightFoot + 1) % 10
            if self.player.speed < self.player.max_speed:
                self.player.speed += 1
            newPositionX = self.player.positionX - self.player.speed
            if 2 not in self.checkPlayerCollisions(newPositionX, self.player.positionY):
                self.player.positionX = newPositionX
            elif newPositionX < self.screen_width/6:
                self.player.positionX = self.screen_width/6
            if self.debug:
                print("move::Action go left")
            self.player.direction = 0

        elif action == 1:
            self.player.rightFoot = (self.player.rightFoot + 1) % 10
            if self.player.speed < self.player.max_speed:
                self.player.speed += 1
            newPositionX = self.player.positionX + self.player.speed
            if not 3 in self.checkPlayerCollisions(newPositionX, self.player.positionY):
                self.player.positionX = newPositionX
            elif newPositionX > self.screen_width/6 * 5 - self.player.playerWidth:
                self.player.positionX = self.screen_width/6 * 5 - self.player.playerWidth
            if self.debug:
                print("move::Action go right")
            self.player.direction = 1

        # TODO: FIX JUMPING REGISTERING TOO FAST TO BE ABLE TO JUMP TWICE
        if action == 2 and self.player.jumpCount < self.player.jump:
            self.player.jumping = True
            self.player.jumpCount += 1
            self.player.jumpPower = -20
            if self.debug:
                print("move::Action jump, power: ", self.player.jumpPower)

    def update(self):
        if self.paused or not self.started or self.dead or self.transition:
            return
        if self.switched:
            self.spawnEnemies()
            self.switched = False
        # Check if the player has gone to a higher tile
        tileGap = 150
        if self.player.positionY < self.newMasterOffset - tileGap and not self.player.jumping:
            self.player.position += 1
            self.newMasterOffset = self.player.positionY + self.player.playerHeight
        if self.newMasterOffset < self.baseY:
            self.masterOffset += 1
            self.newMasterOffset += 1
            self.player.positionY += 1
            for enemy in self.getEnemies():
                enemy.ypos += 1
            for bomb in self.getBombs():
                bomb.positionY += 1
        for bomb in self.getBombs():
            if bomb.positionY < self.newMasterOffset - 40:
                bomb.positionY += 4
            elif bomb.positionY > self.newMasterOffset + 20:
                bomb.positionY += 4

        # Update the screen
        # Update player
        newPositionY = self.player.positionY + self.player.jumpPower
        self.player.jumpPower += 1
        collisions = self.checkPlayerCollisions(self.player.positionX, newPositionY)
        if 1 in collisions:
            temp = self.player.positionY
            while 1 not in self.checkPlayerCollisions(self.player.positionX, newPositionY):
                temp = newPositionY
                newPositionY -= 1
            newPositionY = temp
            self.player.jumpPower = 0
        if 4 in collisions:
            # self.masterOffset = newPositionY
            temp = self.player.positionY
            while 4 not in self.checkPlayerCollisions(self.player.positionX, newPositionY):
                temp = newPositionY
                newPositionY -= 1
            newPositionY = temp
            self.player.jumpPower = 0
            self.player.jumpCount = 0
            self.player.jumping = False
        self.player.positionY = newPositionY

        # Update entities
        for entity in self.entities:
            collide = False

            # PROJECTILE UPDATES =======================================================================================
            if isinstance(entity, Projectile):
                collisions = self.checkProjectileCollisions(entity)
                # Check for horizontal collisions
                if 2 in collisions or 3 in collisions:
                    entity.dirX = -entity.dirX
                    entity.bounce += 1
                    if entity.color != 3:
                        entity.color = (entity.color + 1) % 3
                    collide = True
                # Check for vertical collisions
                if 1 in collisions or 4 in collisions:
                    entity.dirY = -entity.dirY
                    entity.bounce += 1
                    if entity.color != 3:
                        entity.color = (entity.color + 1) % 3


                entity.positionX += entity.speed * entity.dirX
                entity.positionY += entity.speed * entity.dirY
                if entity.bounce > 9\
                    or entity.positionY > self.player.positionY + 2000\
                    or entity.positionY < self.player.positionY - 1000\
                    or entity.positionX > self.player.positionX + 2000\
                    or entity.positionX < self.player.positionX - 1000:
                    self.entities.remove(entity)

                if entity.color == 3\
                    and checkRectangleCollisions(entity.positionX, entity.positionY, entity.size * 2, entity.size * 2,
                                                self.player.positionX, self.player.positionY, self.player.playerWidth, self.player.playerHeight):
                    if not self.player.shield:
                        self.player.health -= 1
                        if self.player.health <= 0:
                            self.dead = True
                    if self.entities.__contains__(entity):
                        self.entities.remove(entity)



            # ITEM UPDATES =============================================================================================
            if isinstance(entity, Item):
                if entity.type == 6:
                    entity.timer += 1
                    if entity.timer == 200:
                        entity.timer = 0
                        x = entity.positionX
                        y = entity.positionY
                        # Bomb explodes in 8 projectiles
                        self.createProjectile(x, y, x + 10, y + 4, 3)
                        self.createProjectile(x, y, x + 10, y + 14, 3)
                        self.createProjectile(x, y, x + 2, y + 14, 3)
                        self.createProjectile(x, y, x - 10, y + 14, 3)
                        self.createProjectile(x, y, x - 10, y, 3)
                        self.createProjectile(x, y, x - 10, y - 14, 3)
                        self.createProjectile(x, y, x - 2, y - 14, 3)
                        self.createProjectile(x, y, x + 10, y - 14, 3)
                        self.entities.remove(entity)
                    continue
                if entity.taken == 0 and entity.type == 7:
                    if self.player.interacted and (self.player.balance >= self.level * 5):
                        self.player.balance -= self.level * 5
                        self.player.interacted = False
                        itm = Item(0, 0, random.randint(1, 4))
                        self.player.add_item(itm)
                        self.last_taken_item = itm
                        entity.taken = 1
                        if itm.type == 1:
                            self.player.max_speed += 1
                        elif itm.type == 2:
                            self.player.jump += 1
                        elif itm.type == 3:
                            self.player.burst += 1
                        elif itm.type == 4:
                            self.player.attack += 1
            # ENEMY UPDATES ============================================================================================
            if isinstance(entity, Enemy):
                entity.timer += 1
                if isinstance(entity, Blob):
                    newxpos = entity.xpos
                    if entity.timer < 25:
                        newxpos +=  1 * entity.direction
                    elif entity.timer < 50:
                        newxpos += 2 * entity.direction
                    elif entity.timer < 75:
                        newxpos += 1 * entity.direction
                    if newxpos < self.screen_width / 6 or newxpos + 40 > self.screen_width / 6 * 5:
                        entity.direction = (-1) * entity.direction
                    else:
                        entity.xpos = newxpos
                    if entity.timer == 200:
                        entity.timer = 0
                        if self.debug:
                            print("update::time in milliseconds: ", pygame.time.get_ticks())
                        self.createProjectile(entity.xpos, entity.ypos, entity.xpos + 100, entity.ypos + 100, 3)
                if entity.timer == 450 and isinstance(entity, Bomber):
                    self.createBomb(entity.xpos + 60, entity.ypos)
                elif entity.timer == 500:
                    entity.timer = 0
                for projectile in self.getProjectiles():
                    if projectile.color == 3:
                        continue
                    if checkRectangleCollisions(entity.xpos, entity.ypos + 20, entity.width, entity.height - 20, projectile.positionX, projectile.positionY, 5, 5):
                        if projectile.color != 3:
                            if self.debug:
                                print("update::entity color vs projectile color: ", str(entity.color) + " " + str(projectile.color))
                            if entity.color == projectile.color:
                                entity.hit(self.player.attack)
                            self.entities.remove(projectile)
                if not entity.alive:
                    self.player.balance += entity.cost
                    self.score += int(entity.cost * 10 / self.level)
                    self.entities.remove(entity)



    def checkPlayerCollisions(self, newX, newY):
        #       1
        #    2  x  3
        #       4
        # Check right collision
        collision = []
        # Check right boundarie collision
        if newX + self.player.playerWidth > (self.screen_width / 6) * 5:
            collision.append(3)
            # Check left boundarie collision
        if newX < self.screen_width / 6:
            collision.append(2)
        if len(collision) != 0:
            return collision

        # Check tile collision
        offsetY = self.masterOffset
        for row in self.getLayout():
            offsetX = self.screen_width / 6
            tileWidth = ( (self.screen_width / 6) * 4 ) / 8
            for tile in row:
                if tile != 0:
                    collision = checkRectangleCollisions(newX, newY, self.player.playerWidth,
                                                         self.player.playerHeight, offsetX, offsetY, tileWidth, 40)
                    if len(collision) != 0:
                        return collision
                offsetX += tileWidth
            offsetY -= 150
        return collision

    def checkProjectileCollisions(self, entity):
        newX = entity.positionX + entity.speed * entity.dirX
        newY = entity.positionY + entity.speed * entity.dirY
        # Check tile collision
        collision = []
        offsetY = self.masterOffset
        if newX + entity.size > (self.screen_width / 6) * 5:
            collision.append(3)
            # Check left boundarie collision
        if newX < self.screen_width / 6:
            collision.append(2)
        if len(collision) != 0:
            return collision

        for row in self.getLayout():
            offsetX = self.screen_width / 6
            tileWidth = int(( (self.screen_width / 6) * 4 ) / 8 + 2)
            for tile in row:
                if tile == 1:
                    collision = checkRectangleCollisions(newX - entity.size, newY - entity.size, entity.size * 2, entity.size  * 2, offsetX, offsetY, tileWidth, 40)
                    if len(collision) != 0:
                        return collision
                offsetX += tileWidth
            offsetY -= 150
        return collision

    def checkItemCollisions(self, item):
        if len(checkRectangleCollisions(self.player.positionX, self.player.positionY, self.player.playerWidth, self.player.playerHeight, item.positionX, item.positionY, 40, 40)) > 0:
            return True
        return False

    def createProjectile(self, posx, posy, goalx, goaly, color):
        # Calculate the trajectory of the projectile

        dirX = goalx - posx
        dirY = goaly - posy

        dx = dirX / (abs(dirX) + abs(dirY))
        dy = dirY / (abs(dirX) + abs(dirY))

        projectile = Projectile(posx, posy, dx, dy, color)
        self.entities.append(projectile)

    def createBomb(self, posx, posy):
        self.entities.append(Item(posx, posy, 6))

    def shoot(self, mouse):
        # Calculate the trajectory of the projectile
        posX = self.player.positionX + self.player.playerWidth / 2 + 10
        posY = self.player.positionY + self.player.playerHeight / 2 + 5

        dirX = mouse[0] - posX
        dirY = mouse[1] - posY

        dx = dirX / (abs(dirX) + abs(dirY))
        dy = dirY / (abs(dirX) + abs(dirY))

        projectile = Projectile(posX, posY, dx, dy, 0)
        self.entities.append(projectile)
        spread = 1
        for i in range(1, self.player.burst):
            spread *= 1.1
            posX = self.player.positionX + self.player.playerWidth / 2
            posY = self.player.positionY + self.player.playerHeight / 2

            dirX = mouse[0] * spread - posX
            dirY = mouse[1] * spread - posY

            dx = dirX / (abs(dirX) + abs(dirY))
            dy = dirY / (abs(dirX) + abs(dirY))

            projectile = Projectile(posX, posY, dx, dy, 0)
            self.entities.append(projectile)

            posX = self.player.positionX + self.player.playerWidth / 2
            posY = self.player.positionY + self.player.playerHeight / 2

            dirX = mouse[0] / spread - posX
            dirY = mouse[1] / spread - posY

            dx = dirX / (abs(dirX) + abs(dirY))
            dy = dirY / (abs(dirX) + abs(dirY))

            projectile = Projectile(posX, posY, dx, dy, 0)
            self.entities.append(projectile)

    def spawnEnemies(self):
        """Spawns a number of entities. Each entity has a spawning cost and there is a certain amount this function
        can spend depending on the level. Higher rows have a higher chance of spawning stronger enemies. Bomber doesn't
        appear until level 2, painter until level 5 and color lord until level 10."""

        layout = self.getLayout()
        offsetY = self.masterOffset
        tileWidth = ((self.screen_width / 6) * 4) / 8
        # index keeps track of the rows, also used to calculate credit amount
        index = 1
        for row in layout:
            offsetX = self.screen_width / 6
            credit = int(index * 0.34) + 1
            taken = []
            while credit > 0:
                tile = random.randint(0, 7)
                while row[tile] == 0 or tile in taken:
                    tile = random.randint(0, 7)
                taken.append(tile)
                X = offsetX + tileWidth * tile
                if index < 5:
                    self.entities.append(Blob(X + 20, offsetY - 40))
                    credit -= Blob.cost
                else:
                    if random.randint(0, 10) < 5:
                        self.entities.append(Blob(X, offsetY - 40))
                        credit -= Blob.cost
                    else:
                        self.entities.append(Bomber(X, offsetY - 100))
                        credit -= Bomber.cost
            offsetY -= 150
            index += 1
            if index == len(layout):
                break



def checkRectangleCollisions(posX, posY, width, height, rPosX, rPosY, rWidth, rHeight):
    """
    Checks if there is a collision between an object and a rectangle.

    :param posX: Horizontal position of the object that is checked for collision .
    :param posY: Vertical position of the object that is checked for collision.
    :param width: Width of the object.
    :param height: Height of the object.
    :param rPosX: Horizontal position of the top left corner of the object that we are testing the collision against.
    :param rPosY: Vertical position of the top left corner of the object that we are testing the collision against.
    :param rWidth: Width of the rectangle we are testing the collision against.
    :param rHeight: Height of the rectangle we are testing the collision against.
    :return: Returns an array of numbers representing collisions (1 - top, 2 - left, 3 - right, 4 - bottom).
    """
    collision = []
    if posX + width > rPosX \
            and (posY < rPosY + rHeight and posY + height > rPosY) \
            and posX < rPosX:
        collision.append(3)
    if posX < rPosX + rWidth \
            and (posY < rPosY + rHeight and posY + height > rPosY) \
            and posX + width > rPosX + rWidth:
        collision.append(2)
    if posY < rPosY + rHeight \
            and (posX + width > rPosX and posX < rPosX + rWidth) \
            and (posY + height > rPosY + rHeight):
        collision.append(1)
    if posY + height > rPosY \
            and (posX + width > rPosX and posX < rPosX + rWidth) \
            and posY < rPosY:
        collision.append(4)

    return collision


