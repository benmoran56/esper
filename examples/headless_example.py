import time

from dataclasses import dataclass as component

import esper


##################################
#  Define some Components:
##################################
@component
class Velocity:
    x: float = 0.0
    y: float = 0.0


@component
class Position:
    x: int = 0
    y: int = 0


################################
#  Define some Processors:
################################
class MovementProcessor:
    def process(self):
        for ent, (vel, pos) in esper.get_components(Velocity, Position):
            pos.x += vel.x
            pos.y += vel.y
            print("Current Position: {}".format((int(pos.x), int(pos.y))))


##########################################################
# Instantiate everything, and create your main logic loop:
##########################################################
def main():
    # Instantiate a Processor (or more), and add them to the world:
    movement_processor = MovementProcessor()

    # Create entities, and assign Component instances to them:
    player = esper.create_entity()
    esper.add_component(player, Velocity(x=0.9, y=1.2))
    esper.add_component(player, Position(x=5, y=5))

    # A dummy main loop:
    try:
        while True:
            # Call esper.process() to run all Processors.
            movement_processor.process()
            time.sleep(1)

    except KeyboardInterrupt:
        return


if __name__ == '__main__':
    print("\nHeadless Example. Press Ctrl+C to quit!\n")
    main()
