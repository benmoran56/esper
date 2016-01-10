import pyglet
import esper


FPS = 60
RESOLUTION = 720, 480


##################################
#  Define some Components:
##################################
class Velocity:
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y


class Renderable:
    def __init__(self, sprite):
        self.sprite = sprite
        self.w = sprite.width
        self.h = sprite.height


################################
#  Define some Processors:
################################
class MovementProcessor(esper.Processor):
    def __init__(self, minx, maxx, miny, maxy):
        super().__init__()
        self.minx = minx
        self.miny = miny
        self.maxx = maxx
        self.maxy = maxy

    def process(self, dt):
        # This will iterate over every Entity that has BOTH of these components:
        for ent, (vel, rend) in self.world.get_components(Velocity, Renderable):
            # Update the Renderable Component's position by it's Velocity:
            # An example of keeping the sprite inside screen boundaries. Basically,
            # adjust the position back inside screen boundaries if it tries to go outside:
            new_x = max(self.minx, rend.sprite.x + vel.x)
            new_y = max(self.miny, rend.sprite.y + vel.y)
            new_x = min(self.maxx - rend.w, new_x)
            new_y = min(self.maxy - rend.h, new_y)
            rend.sprite.position = new_x, new_y


class RenderProcessor(esper.Processor):
    def __init__(self, window, batch):
        super().__init__()
        self.window = window
        self.batch = batch

    def process(self, dt):
        self.window.clear()
        self.batch.draw()


###############################################
#  Initialize pyglet window and graphics batch:
###############################################
window = pyglet.window.Window(width=RESOLUTION[0], height=RESOLUTION[1], caption="Esper pyglet example")
batch = pyglet.graphics.Batch()

# Initialize Esper world, and create a "player" Entity with a few Components.
world = esper.World()
player = world.create_entity()
world.add_component(player, Velocity(x=0, y=0))
world.add_component(player, Renderable(sprite=pyglet.sprite.Sprite(pyglet.image.load("redsquare.png"),
                                                                   x=100, y=100, batch=batch)))
# Another motionless Entity:
enemy = world.create_entity()
world.add_component(enemy, Renderable(sprite=pyglet.sprite.Sprite(pyglet.image.load("bluesquare.png"),
                                                                  x=400, y=250, batch=batch)))

# Create some Processor instances, and asign them to be processed.
movement_processor = MovementProcessor(minx=0, miny=0, maxx=RESOLUTION[0], maxy=RESOLUTION[1])
render_processor = RenderProcessor(window=window, batch=batch)
world.add_processor(movement_processor)
world.add_processor(render_processor)


##############################
#  Pyglet events for movement:
##############################
@window.event
def on_key_press(key, mod):
    if key == pyglet.window.key.RIGHT:
        world.component_for_entity(player, Velocity).x = 3
    if key == pyglet.window.key.LEFT:
        world.component_for_entity(player, Velocity).x = -3
    if key == pyglet.window.key.UP:
        world.component_for_entity(player, Velocity).y = 3
    if key == pyglet.window.key.DOWN:
        world.component_for_entity(player, Velocity).y = -3


@window.event
def on_key_release(key, mod):
    if key in (pyglet.window.key.RIGHT, pyglet.window.key.LEFT):
        world.component_for_entity(player, Velocity).x = 0
    if key in (pyglet.window.key.UP, pyglet.window.key.DOWN):
        world.component_for_entity(player, Velocity).y = 0


if __name__ == "__main__":
    # NOTE!  schedule_interval will automatically pass a "delta time" argument
    #        to world.process, so you must make sure that your Processor classes
    #        account for this. See the example Processors above for an example.
    pyglet.clock.schedule_interval(world.process, interval=1.0/FPS)
    pyglet.app.run()
