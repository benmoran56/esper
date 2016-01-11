#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals

import sys

import pyglet
from pyglet.window import key

import esper


FPS = 60
RESOLUTION = 720, 480
BGCOLOR = (0, 0, 0, 255)


##################################
#  Define some Components:
##################################
class Velocity(object):
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y


class Renderable(object):
    def __init__(self, image, width, height, posx, posy, group=None):
        self.image = image
        self.x = posx
        self.y = posy
        self.w = width
        self.h = height
        self.group = group


################################
#  Define some Processors:
################################
class MovementProcessor(esper.Processor):
    def __init__(self, minx, maxx, miny, maxy):
        super(MovementProcessor, self).__init__()
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


class SpriteRenderProcessor(esper.Processor):
    def __init__(self, batch):
        super(SpriteRenderProcessor, self).__init__()
        self.batch = batch

    def process(self):
        # This will iterate over every Entity that has this Component, and
        # add the texture associated with the Renderable Component instance
        # and its vertice_list to the render batch. The batch will then be
        # drawn by the 'on_draw' event handler of teh main window:
        for ent, rend in self.world.get_component(Renderable):
            if not hasattr(rend, '_sprite'):
                rend._sprite = pyglet.sprite.Sprite(rend.image, rend.x, rend.y,
                    batch=self.batch, group=rend.group)
            else:
                rend._sprite.x = rend.x
                rend._sprite.y = rend.y


################################
#  The main core of the program:
################################
def run(args=None):
    # Initialize the main window stuff
    window = pyglet.window.Window(width=RESOLUTION[0], height=RESOLUTION[1])
    window.set_caption("Esper pyglet Example")
    pyglet.gl.glClearColor(*BGCOLOR)
    # OpenGL graphics batch
    renderbatch = pyglet.graphics.Batch()

    # Initialize Esper world, and create a "player" Entity with a few Components.
    world = esper.World()
    player = world.create_entity()
    world.add_component(player, Velocity(x=0, y=0))
    redsquare = Renderable(
        image=pyglet.resource.image("redsquare.png"),
        width=64,
        height=64,
        posx=100,
        posy=100)
    world.add_component(player, redsquare)

    # Another motionless Entity:
    enemy = world.create_entity()
    bluesquare = Renderable(
        image=pyglet.resource.image("bluesquare.png"),
        width=64,
        height=64,
        posx=400,
        posy=250)
    world.add_component(enemy, bluesquare)

    # Create some Processor instances, and asign them to be processed.
    render_processor = SpriteRenderProcessor(renderbatch)
    movement_processor = MovementProcessor(minx=0, maxx=RESOLUTION[0], miny=0,
                                           maxy=RESOLUTION[1])
    world.add_processor(render_processor)
    world.add_processor(movement_processor)

    @window.event
    def on_key_press(symbol, modifiers):
        if symbol == key.UP:
            # Here is a way to directly access a specific Entity's Velocity
            # Component's attribute (y) without making a temporary variable.
            world.component_for_entity(player, Velocity).y = 3
        elif symbol == key.DOWN:
            # For clarity, here is an alternate way in which a temporary variable
            # is created and modified. The previous way above is recommended instead.
            player_velocity_component = world.component_for_entity(player, Velocity)
            player_velocity_component.y = -3
        elif symbol == key.LEFT:
            world.component_for_entity(player, Velocity).x = -3
        elif symbol == key.RIGHT:
            world.component_for_entity(player, Velocity).x = 3
        elif symbol == key.ESCAPE:
            pyglet.app.exit()

    @window.event
    def on_key_release(symbol, modifiers):
        if symbol in (key.UP, key.DOWN):
            world.component_for_entity(player, Velocity).y = 0
        if symbol in (key.LEFT, key.RIGHT):
            world.component_for_entity(player, Velocity).x = 0

    @window.event
    def on_draw():
        # Clear the window:
        window.clear()
        # Draw renderables
        renderbatch.draw()

    def update(dt):
        # A single call to world.process() will update all Processors:
        world.process()

    pyglet.clock.schedule_interval(update, 1.0 / FPS)
    pyglet.app.run()


if __name__ == "__main__":
    import sys
    sys.exit(run(sys.argv[1:]) or 0)
