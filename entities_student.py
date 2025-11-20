# -*- coding: utf-8 -*-
import pygame
from pygame import Surface
from config import TILE_SIZE, PLAYER_SPEED, RUN_MULTIPLIER, PLAYER_ACCEL, PLAYER_FRICTION, WHITE, BLUE, GREEN, YELLOW, RED, FONT_SIZE
class Player(pygame.sprite.Sprite):
    def __init__(self, pos_px):
        super().__init__()
        self.image = Surface((TILE_SIZE-6, TILE_SIZE-6), pygame.SRCALPHA)
        self.image.fill(BLUE)
        self.rect = self.image.get_rect(topleft=pos_px)
        self.vel = pygame.math.Vector2(0, 0)
    def handle_input(self, keys, running: bool):
        dir = pygame.math.Vector2(0, 0)
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:  dir.x -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dir.x += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:    dir.y -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:  dir.y += 1
        if dir.length_squared() > 0:
            dir = dir.normalize()
        speed = PLAYER_SPEED
        # TODO: Shiftで走る
        # if running: speed *= RUN_MULTIPLIER
        # TODO: 慣性＋摩擦
        # self.vel.x = self.vel.x*(1-PLAYER_ACCEL) + dir.x*speed*PLAYER_ACCEL
        # self.vel.y = self.vel.y*(1-PLAYER_ACCEL) + dir.y*speed*PLAYER_ACCEL
        # self.vel *= PLAYER_FRICTION
        self.vel.x = dir.x*speed
        self.vel.y = dir.y*speed
    def move_free(self):
        self.rect.x += int(self.vel.x)
        self.rect.y += int(self.vel.y)
    def move_with_collision(self, grid, collides_fn):
        self.rect.x += int(self.vel.x)
        if collides_fn(self.rect, grid):
            self.rect.x -= int(self.vel.x)
        self.rect.y += int(self.vel.y)
        if collides_fn(self.rect, grid):
            self.rect.y -= int(self.vel.y)
    def update(self, grid, keys, running, collides_fn=None):
        self.handle_input(keys, running)
        if collides_fn is None:
            self.move_free()
        else:
            self.move_with_collision(grid, collides_fn)
class Camera:
    def __init__(self, screen_size):
        self.offset = pygame.math.Vector2(0, 0)
        self.screen_w, self.screen_h = screen_size
    def follow(self, target_rect):
        self.offset.x = max(0, target_rect.centerx - self.screen_w//2)
        self.offset.y = max(0, target_rect.centery - self.screen_h//2)
class HUD:
    def __init__(self):
        self.font = pygame.font.SysFont(None, FONT_SIZE)
        self.msg = ""; self.timer = 0
    def toast(self, text, frame=120):
        self.msg = text; self.timer = frame
    def render(self, screen):
        if self.timer > 0 and self.msg:
            surf = self.font.render(self.msg, True, WHITE)
            screen.blit(surf, (16, 12))
            self.timer -= 1
class NPC(pygame.sprite.Sprite):
    def __init__(self, pos_px):
        super().__init__()
        self.image = Surface((TILE_SIZE-6, TILE_SIZE-6), pygame.SRCALPHA)
        self.image.fill(GREEN)
        self.rect = self.image.get_rect(topleft=pos_px)
