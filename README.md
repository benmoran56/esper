Esper
=====
**Esper is a lightweight Entity System for Python, designed with a focus on performance.**

The design is based on the Entity System concepts described by Adam Martin in his blog at
T-Machines.org, and others.

Esper takes inspiration by Sean Fisk's **ecs** https://github.com/seanfisk/ecs,
and Martin Von Appen's **ebs** https://bitbucket.org/marcusva/python-utils.


Compatibility
-------------
Esper is developed for Python 3, and is also know to work on Pypy3.
Python 2 is not supported, due to differences in dictionary key iteration. It can be
made to work with a little effort, but official support is not planned.


Usage
-----
Esper is a tiny library, and is intended to be dropped directly into your project.
Simply copy the *esper* directory into the top level of your project folder, and
*import esper*. See the *examples* folder for more details.

A short code snipped showing the bare basics::

    # Create a World instance to hold everything:
    world = esper.World()

    # Instantiate a Processor (or more), and add them to the world:
    movement_processor = MovementProcessor()
    world.add_processor(movement_processor)

    # Create entities, and assign Component instances to them:
    player = world.create_entity()
    world.add_component(player, Velocity(x=0.9, y=1.2))
    world.add_component(player, Position(x=5, y=5))

    # Processors can query components as such:
    for ent, (vel, pos) in self.world.get_components(Velocity, Position):
        pass


