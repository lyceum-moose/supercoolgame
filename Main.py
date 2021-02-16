import os
import pygame
import random
import time
import sqlite3


class lvlConst:
    def __init__(self):
        self.Height = 500
        self.Width = 500
        self.stock = 50
        self.les = 125
        self.Bottom = 400


class Direction:
    def __init__(self):
        self.up = 1
        self.down = 2
        self.left = 3
        self.right = 4
        self.no = 5


class BaseSprite(pygame.sprite.Sprite):
    def __init__(self, location, files):
        super(BaseSprite, self, ).__init__()
        self.index = 0
        self.images = []
        for i in range(len(files)):
            self.images.append(self.getImage(files[i]))
        if self.images.__len__() > 0:
            self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.location = location
        self.rect.left, self.rect.top = location
        self.direction = 1

    def update(self):
        self.index += 1
        if self.index >= len(self.images):
            self.index = 0
        self.image = self.images[self.index]
        self.image.set_colorkey((255, 255, 255))

    def setCoords(self, x, y):
        self.rect.x = x
        self.rect.y = y

    def moveRight(self, pixels):
        self.rect.x += pixels

    def moveLeft(self, pixels):
        self.rect.x -= pixels

    def moveUp(self, pixels):
        self.rect.y -= pixels

    def modeDown(self, pixels):
        self.rect.y += pixels

    def getImage(self, name):
        fullname = f"{os.getcwd()}\\src\\{name}"
        image = pygame.image.load(fullname).convert_alpha()
        return image

    def checkCol(self, sprite):
        return pygame.sprite.collide_rect(self, sprite)


class Background(BaseSprite):
    def __init__(self, location, files):
        super(Background, self).__init__(location, files)


class Player(BaseSprite):
    def __init__(self, location, files):
        super(Player, self).__init__(location, files)
        self.health = 30
        self.ledx = 0
        self.keycard = 0
        self.stand = False;
        self.drowning = False;

    def update(self):
        self.index += 1
        if self.index >= len(self.images):
            self.index = 0
        self.image = self.images[self.index]
        if not self.stand:
            self.modeDown(2)
        if not self.stand and self.drowning:
            self.moveUp(1)


class Wild(BaseSprite):
    def __init__(self, location, files):
        super(Wild, self).__init__(location, files)
        self.direction = 1
        self.speed = 5

    def update(self):
        if self.rect.x < 0 or self.rect.x > 420:
            self.direction *= -1
            self.index += 1
        self.moveRight(self.speed * self.direction)
        if self.index >= len(self.images):
            self.index = 0
        self.image = self.images[self.index]
        self.image.set_colorkey((255, 255, 255))


class Bunker(BaseSprite):
    def __init__(self, location, files):
        super(Bunker, self).__init__(location, files)

    def update(self):
        if self.index >= len(self.images):
            self.index = 0
        self.image = self.images[self.index]


class Ledx(BaseSprite):
    def __init__(self, location, files):
        super(Ledx, self).__init__(location, files)


class Keycard(BaseSprite):
    def __init__(self, location, files):
        super(Keycard, self).__init__(location, files)


class Update_Mes(BaseSprite):
    def __init__(self, location, files):
        super(Update_Mes, self).__init__(location, files)


class BaseScene:
    def __init__(self):
        pygame.display.set_caption('Gamedev Simulator 2021')
        self.started = False
        self.FPS = 60
        self.DEBUG = False
        self.seconds = 0
        self.clock = pygame.time.Clock()
        self.lvlConst = lvlConst()
        self.paused = False
        self.screen = pygame.display.set_mode((self.lvlConst.Width, self.lvlConst.Height))
        pygame.init()

    def main(self):
        self.started = False

    def start(self):
        self.started = True
        ticks = 0
        while self.started:
            self.main()
            if not self.paused:
                ticks += 1
                self.clock.tick(self.FPS)
                self.seconds += (ticks % self.FPS) / 1000
                self.myGroup.update()
                self.myGroup.draw(self.screen)
                pygame.display.flip()


class Menu(BaseScene):
    def __init__(self):
        super(Menu, self).__init__()
        self.background = BaseSprite([0, 0], ["Menu.png"])
        self.newGame = BaseSprite([50, 150], ["Start.png"])
        self.exit = BaseSprite([50, 350], ["Exit.png"])
        self.myGroup = pygame.sprite.Group(
            self.background,
            self.newGame,
            self.exit
        )

    def main(self):
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if self.exit.rect.collidepoint(pos):
                    self.started = False
                if self.newGame.rect.collidepoint(pos):
                    self.started = False
                    gameScene = GameScene()
                    gameScene.start()
        pygame.display.flip()


class GameScene(BaseScene):
    def __init__(self):
        super(GameScene, self).__init__()
        self.start_time = time.clock()
        self.les = BaseSprite([0, self.lvlConst.les + 50], ["les.jpg"])
        self.sand = BaseSprite([0, self.lvlConst.Bottom + 40], ["Bottom.jpg"])
        self.stock = BaseSprite([0, 0], ["stock.jpg"])
        self.bunker = Bunker([200, self.lvlConst.les - 30], ["Bunker1.jpg"])
        self.player = Player([250, self.lvlConst.les], ["1.jpg"])
        self.wild = Wild([0, 250], ["wild1.jpg", "wild2.jpg"])
        self.keycard = Keycard([100, self.lvlConst.Bottom], ["Keycard.png"])
        self.ledx = Ledx([300, self.lvlConst.Bottom], ["Ledx.png"])
        self.upgrade_mes = Update_Mes([200, 200], ["can_upgrade.png"])
        self.keycardCollected = False
        self.ledxCollected = False
        self.stage = 0
        self.has_warning = True
        self.stages = [[5, 5], [10, 10], [15, 15], [16, 16]]
        self.myGroup = pygame.sprite.Group(
            self.stock,
            self.les,
            self.sand,
            self.wild,
            self.keycard,
            self.ledx,
            self.bunker,
            self.player,
        )

    def main(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.started = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.started = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    self.paused = not self.paused
        if not self.paused:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE]:
                self.started = False
                menuScene = Menu()
                menuScene.start()

            if keys[pygame.K_LEFT] and self.player.rect.x > 0:
                self.player.moveLeft(5)
            if keys[pygame.K_RIGHT] and self.player.rect.x < 450:
                self.player.moveRight(5)
            if keys[pygame.K_UP] and self.player.rect.y > 0:
                self.player.moveUp(5)
            if keys[pygame.K_DOWN] and self.player.rect.y < 450:
                self.player.modeDown(5)

            if keys[pygame.K_u]:
                if self.player.ledx >= self.stages[self.stage][0] and self.player.keycard >= self.stages[self.stage][1]:
                    self.player.ledx -= self.stages[self.stage][0]
                    self.player.keycard -= self.stages[self.stage][1]
                    self.stage += 1
                    self.myGroup.remove([self.bunker])
                    self.bunker = Bunker([200, self.lvlConst.les - 50], ["Bunker" + str(self.stage + 1) + ".jpg"])
                    self.myGroup.add(self.bunker)
                    self.wild.speed += 2
                    self.has_warning = True

            if self.player.checkCol(self.wild):
                self.player.health -= 1

            self.player.drowning = self.player.checkCol(self.les)
            self.player.stand = self.player.checkCol(self.bunker) or self.player.checkCol(self.sand)

            if self.player.checkCol(self.keycard):
                self.player.keycard += 1
                self.keycardCollected = True
                self.keycard.moveRight(500)

            if self.player.checkCol(self.ledx):
                self.player.ledx += 1
                self.ledxCollected = True
                self.ledx.moveRight(500)

            if self.stage == 3:
                self.started = False
                con = sqlite3.connect("data/users.sqlite")
                cur = con.cursor()
                cur.execute(f"""INSERT INTO users VALUES('cooluser', '{time.clock() - self.start_time}')""")
                con.commit()
                success = Success(self.seconds)
                success.start()

            if self.keycardCollected and self.player.checkCol(self.bunker):
                self.keycardCollected = False
                self.keycard.setCoords(random.randint(50, 450), 400)
            if self.ledxCollected and self.player.checkCol(self.bunker):
                self.ledxCollected = False
                self.ledx.setCoords(random.randint(50, 450), 400)
            if self.player.ledx >= self.stages[self.stage][0] and self.player.keycard >= self.stages[self.stage][
                1] and self.has_warning:
                self.myGroup.add([self.upgrade_mes])
                time.sleep(3)
                self.myGroup.remove(self.upgrade_mes)
                self.has_warning = False

            if self.player.health == 0:
                newOver = GameOver()
                newOver.start()
                self.started = False


class GameOver(BaseScene):
    def __init__(self):
        super(GameOver, self).__init__()
        self.background = BaseSprite([0, 0], ["gameover.png"])
        self.tryAgain = BaseSprite([50, 300], ["again.png"])
        self.myGroup = pygame.sprite.Group(
            self.background,
            self.tryAgain
        )

    def main(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.started = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.started = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if self.tryAgain.rect.collidepoint(pos):
                    self.started = False
                    newScene = GameScene()
                    newScene.start()
        pygame.display.flip()


class Success(BaseScene):
    def __init__(self, score):
        super(Success, self).__init__()
        self.score = score
        self.background = BaseSprite([0, 0], ["Success.png"])
        self.tryAgain = BaseSprite([50, 300], ["again.png"])

    def main(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.started = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if self.back.rect.collidepoint(pos):
                    self.started = False
                    Menu().start()
        pygame.display.flip()


if __name__ == '__main__':
    pygame.mixer.init()
    pygame.mixer.music.load('cybersport.mp3')
    pygame.mixer.music.play(-1)
    menuScene = Menu()
    menuScene.start()
    pygame.quit()
