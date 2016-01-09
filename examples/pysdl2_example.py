from sdl2 import *
import sdl2.ext as ext
import esper


RESOLUTION = 720, 480


##################################
#  Define some Components:
##################################
class Velocity:
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y


class Renderable:
    def __init__(self, texture, width, height, posx, posy):
        self.texture = texture
        self.x = posx
        self.y = posy
        self.w = width
        self.h = height


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
    def __init__(self, renderer, clear_color=(0, 0, 0)):
        super().__init__()
        self.renderer = renderer
        self.clear_color = clear_color

    def process(self):
        # Clear the window:
        self.renderer.clear(self.clear_color)
        # Create a destination Rect for the texture:
        destination = SDL_Rect(0, 0, 0, 0)
        # This will iterate over every Entity that has this Component, and blit it:
        for ent, rend in self.world.get_component(Renderable):
            destination.x = int(rend.x)
            destination.y = int(rend.y)
            destination.w = rend.w
            destination.h = rend.h
            SDL_RenderCopy(self.renderer.renderer, rend.texture, None, destination)
        self.renderer.present()


################################
#  Some SDL2 Functions:
################################
def texture_from_image(renderer, image_name):
    """Create an SDL2 Texture from an image file"""
    soft_surface = ext.load_image(image_name)
    texture = SDL_CreateTextureFromSurface(renderer.renderer, soft_surface)
    SDL_FreeSurface(soft_surface)
    return texture


################################
#  The main core of the program:
################################
def run():
    # Initialize PySDL2 stuff
    ext.init()
    window = ext.Window(title="Esper PySDL2 example", size=RESOLUTION)
    renderer = ext.Renderer(target=window)
    window.show()

    # Initialize Esper world, and create a "player" Entity with a few Components.
    world = esper.World()
    player = world.create_entity()
    world.add_component(player, Velocity(x=0, y=0))
    world.add_component(player, Renderable(texture=texture_from_image(renderer, "redsquare.png"),
                                           width=64, height=64, posx=100, posy=100))
    # Another motionless Entity:
    enemy = world.create_entity()
    world.add_component(enemy, Renderable(texture=texture_from_image(renderer, "bluesquare.png"),
                                          width=64, height=64, posx=400, posy=250))

    # Create some Processor instances, and asign them to be processed.
    render_processor = RenderProcessor(renderer=renderer)
    movement_processor = MovementProcessor(minx=0, maxx=RESOLUTION[0], miny=0, maxy=RESOLUTION[1])
    world.add_processor(render_processor)
    world.add_processor(movement_processor)

    # A simple main loop
    running = True
    while running:
        start_time = SDL_GetTicks()

        for event in ext.get_events():
            if event.type == SDL_QUIT:
                running = False
                break
            if event.type == SDL_KEYDOWN:
                if event.key.keysym.sym == SDLK_UP:
                    # Here is a way to directly access a specific Entity's Velocity
                    # Component's attribute (y) without making a temporary variable.
                    world.component_for_entity(player, Velocity).y = -3
                elif event.key.keysym.sym == SDLK_DOWN:
                    # For clarity, here is an alternate way in which a temporary variable
                    # is created and modified. The previous way above is recommended instead.
                    player_velocity_component = world.component_for_entity(player, Velocity)
                    player_velocity_component.y = 3
                elif event.key.keysym.sym == SDLK_LEFT:
                    world.component_for_entity(player, Velocity).x = -3
                elif event.key.keysym.sym == SDLK_RIGHT:
                    world.component_for_entity(player, Velocity).x = 3
                elif event.key.keysym.sym == SDLK_ESCAPE:
                    running = False
                    break
            elif event.type == SDL_KEYUP:
                if event.key.keysym.sym in (SDLK_UP, SDLK_DOWN):
                    world.component_for_entity(player, Velocity).y = 0
                if event.key.keysym.sym in (SDLK_LEFT, SDLK_RIGHT):
                    world.component_for_entity(player, Velocity).x = 0

        # A single call to world.process() will update all Processors:
        world.process()

        # A crude FPS limiter for about 60fps
        current_time = SDL_GetTicks()
        sleep_time = int(start_time + 16.667 - current_time)
        if sleep_time > 0:
            SDL_Delay(sleep_time)

if __name__ == "__main__":
    run()
    ext.quit()
