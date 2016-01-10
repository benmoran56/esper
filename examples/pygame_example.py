#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals

import pygame

import esper


RESOLUTION = 720, 480


##################################
#  Define some Components:
##################################
class Velocity(object):
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y


class Renderable(object):
    def __init__(self, image, posx, posy, depth=0):
        self.image = image
        self.depth = depth
        self.x = posx
        self.y = posy
        self.w = image.get_width()
        self.h = image.get_height()


################################
#  Define some Processors:
################################
class MovementProcessor(esper.Processor):
    def __init__(self, minx, maxx, miny, maxy):
        super().__init__()
        self.minx = minx
        self.maxx = maxx
        self.miny = miny
        self.maxy = maxy

    def process(self):
        # This will iterate over every Entity that has BOTH of these components:
        for ent, (vel, rend) in self.world.get_components(Velocity, Renderable):
            # Update the Renderable Component's position by it's Velocity:
            rend.x += vel.x
            rend.y += vel.y
            # An example of keeping the sprite inside screen boundaries. Basically,
            # adjust the position back inside screen boundaries if it tries to go outside:
            rend.x = max(self.minx, rend.x)
            rend.y = max(self.miny, rend.y)
            rend.x = min(self.maxx - rend.w, rend.x)
            rend.y = min(self.maxy - rend.h, rend.y)


class RenderProcessor(esper.Processor):
    def __init__(self, window, clear_color=(0, 0, 0)):
        super().__init__()
        self.window = window
        self.clear_color = clear_color

    def process(self):
        # Clear the window:
        self.window.fill(self.clear_color)
        # This will iterate over every Entity that has this Component, and blit it:
        for ent, rend in self.world.get_component(Renderable):
            self.window.blit(rend.image, (rend.x, rend.y))
        # Flip the framebuffers
        pygame.display.flip()


################################
#  The main core of the program:
################################
def run():
    # Initialize Pygame stuff
    pygame.init()
    window = pygame.display.set_mode(RESOLUTION)
    pygame.display.set_caption("Esper Pygame example")
    clock = pygame.time.Clock()
    pygame.key.set_repeat(1, 1)

    # Initialize Esper world, and create a "player" Entity with a few Components.
    world = esper.World()
    player = world.create_entity()
    world.add_component(player, Velocity(x=0, y=0))
    world.add_component(player, Renderable(image=pygame.image.load("redsquare.png"), posx=100, posy=100))
    # Another motionless Entity:
    enemy = world.create_entity()
    world.add_component(enemy, Renderable(image=pygame.image.load("bluesquare.png"), posx=400, posy=250))

    # Create some Processor instances, and asign them to be processed.
    render_processor = RenderProcessor(window=window)
    movement_processor = MovementProcessor(minx=0, maxx=RESOLUTION[0], miny=0, maxy=RESOLUTION[1])
    world.add_processor(render_processor)
    world.add_processor(movement_processor)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        keys_pressed = pygame.key.get_pressed()

        if keys_pressed[pygame.K_LEFT]:
            # Here is a way to directly access a specific Entity's Velocity
            # Component's attribute (y) without making a temporary variable.
            world.component_for_entity(player, Velocity).x = -3
        if keys_pressed[pygame.K_RIGHT]:
            # For clarity, here is an alternate way in which a temporary variable
            # is created and modified. The previous way above is recommended instead.
            player_velocity_component = world.component_for_entity(player, Velocity)
            player_velocity_component.y = 3
        if keys_pressed[pygame.K_UP]:
            world.component_for_entity(player, Velocity).y = -3
        if keys_pressed[pygame.K_DOWN]:
            world.component_for_entity(player, Velocity).y = 3
        if keys_pressed[pygame.K_ESCAPE]:
            running = False

        # A single call to world.process() will update all Processors:
        world.process()

        clock.tick(60)


if __name__ == "__main__":
    run()
    pygame.quit()
