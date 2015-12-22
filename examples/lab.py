import sys
import time
import esper

world = esper.World()


class Velocity(esper.Component):
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y


class Position(esper.Component):
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y


class MovementProcessor(esper.Processor):
    def process(self):
        for e, v in self.world.get_component(Velocity):
            print(e, v)


#######################################################

player = world.create_entity()
enemy = world.create_entity()
world.add_component(player, Velocity())
world.add_component(player, Position())
world.add_component(enemy, Velocity())
world.add_component(enemy, Position())

movement_processor = MovementProcessor()
world.add_processor(movement_processor)

start = time.time()
try:
    while True:
        # Runs the update() method of all added systems.
        world.process()
        time.sleep(1)
        now = time.time()
        elapsed = now - start
        start = now
except KeyboardInterrupt:
    sys.exit()


