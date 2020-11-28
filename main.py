import pygame
import sys
from math import sin, cos, atan, pi
import random
from random import randint, uniform


class Player:
    def __init__(self):
        self.rect = pygame.Rect((screen_width - player_size) // 2, (screen_height - player_size) // 2, player_size, player_size)
        self.speed = 5
        self.rotate_speed = 0.05
        self.alpha = uniform(0, 2 * pi)

    @staticmethod
    def get_alpha(x_move, y_move):
        if x_move != 0:
            alpha = atan(abs(y_move / x_move))
            if x_move < 0:
                alpha = pi - alpha
            if y_move < 0:
                alpha = 2 * pi - alpha
            return alpha
        if y_move > 0:
            return pi / 2
        elif y_move < 0:
            return 3 * pi / 2
        return None

    def add_point(self, points, alpha):
        points.append((player_size * cos(alpha) + self.rect.centerx, player_size * sin(alpha) + self.rect.centery))

    def update(self, mouse_x, mouse_y, camera):
        x_move, y_move = mouse_x - self.rect.centerx, mouse_y - self.rect.centery
        if abs(x_move) < player_size / 2:
            x_move = 0
        if abs(y_move) < player_size / 2:
            y_move = 0
        alpha = self.get_alpha(x_move, y_move)
        if alpha is None:
            return
        if alpha > self.alpha:
            if alpha - self.alpha < pi:
                self.alpha += self.rotate_speed
            else:
                self.alpha -= self.rotate_speed
        else:
            if self.alpha - alpha < pi:
                self.alpha -= self.rotate_speed
            else:
                self.alpha += self.rotate_speed
        self.alpha %= 2 * pi
        alpha = self.alpha
        camera.move(cos(alpha) * self.speed, sin(alpha) * self.speed)

    def draw(self, surface):
        points = []
        alpha = self.alpha
        self.add_point(points, alpha)
        alpha += 3 * pi / 4
        self.add_point(points, alpha)
        alpha += pi / 2
        self.add_point(points, alpha)
        pygame.draw.polygon(surface, player_color, points)


class Camera:
    def __init__(self, coord):
        self.attach_x = coord[0]
        self.attach_y = coord[1]
        self.d_x = 0
        self.d_y = 0

    def move(self, d_x, d_y):
        self.d_x += d_x
        self.d_y += d_y

    def apply(self, coord):
        return self.attach_x + coord[0] - self.d_x, self.attach_y + coord[1] - self.d_y

    def get_pos(self):
        return self.d_x, self.d_y


class Item:
    def __init__(self):
        if random.random() < (screen_height + 2 * appear_area) / (screen_height + screen_width + 4 * appear_area):
            # Лево и право с углами
            pos_x = random.choice([-1, 1]) * (screen_width // 2 + randint(0, appear_area))
            pos_y = randint(-screen_height // 2 - appear_area, screen_height // 2 + appear_area)
        else:
            # Верх и низ без углов
            pos_y = random.choice([-1, 1]) * (screen_height // 2 + randint(0, appear_area))
            pos_x = randint(-screen_width // 2, screen_width // 2)

        pos_x += camera.d_x
        pos_y += camera.d_y
        self.rect = pygame.Rect(pos_x, pos_y, item_size, item_size)
        self.image = pygame.Surface((2 * item_size, 2 * item_size))
        self.image.fill(bg_color)
        pygame.draw.circle(self.image, item_color, (item_size, item_size), item_size)

    def to_remove(self):
        x_i, y_i = self.rect.center
        x_p, y_p = camera.get_pos()
        if x_i > x_p + screen_width / 2 + appear_area:
            return True
        if x_i < x_p - screen_width / 2 - appear_area:
            return True
        if y_i > y_p + screen_height / 2 + appear_area:
            return True
        if y_i < y_p - screen_height / 2 - appear_area:
            return True
        return False

    def draw(self, surface, camera):
        surface.blit(self.image, camera.apply(self.rect.center))


pygame.init()
clock = pygame.time.Clock()

bg_color = pygame.Color('grey12')
player_color = pygame.Color('blue')
item_color = pygame.Color('yellow')

screen_width = 1280
screen_height = 720
fps = 60

player_size = 40
item_size = 5
max_items = 1000
appear_area = 1000

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Good game!")

player = Player()
camera = Camera(player.rect.center)
items = set()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()
    while len(items) < max_items:
        items.add(Item())
    x_mouse, y_mouse = pygame.mouse.get_pos()
    player.update(x_mouse, y_mouse, camera)
    screen.fill(bg_color)
    to_remove = set()
    for item in items:
        if item.to_remove():
            to_remove.add(item)
        item.draw(screen, camera)
    items -= to_remove
    player.draw(screen)

    pygame.display.flip()
    clock.tick(fps)
