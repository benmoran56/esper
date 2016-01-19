Esper
=====
**Esper is a lightweight Entity System for Python, with a focus on performance.**

The design is based on the Entity System concepts described by Adam Martin in his blog at
T-Machines.org, and others. Efforts were made to keep it as lightweight and performant as possible.

Inspired by Sean Fisk's **ecs** https://github.com/seanfisk/ecs,
and Marcus von Appen's **ebs** https://bitbucket.org/marcusva/python-utils.


What's New
----------

**0.9.2** - Switched to a different database structure internally. (No API changes)
            There are now examples for pyglet, Pygame, and PySDL2.
            Thanks to Christopher Arndt, multiple component queries are faster.

**0.9.0** - Esper should now be fully usable for your game or program.
            Example code for Pygame and PySDL. Pyglet example coming soon!


1) Compatibility
----------------
Esper is developed for Python 3. It is also know to work on Pypy3. Being written in pure
Python, it should work on any compliant interpreter. Python 2 is not supported in the main
branch for now, but Christopher Arndt is currently maintaining a branch here:
https://github.com/SpotlightKid/esper/tree/python2

2) Installation
---------------
No installation is necessary. Esper is a tiny library with no dependencies. Simply copy
the *esper* directory into the top level of your project folder, and *import esper*.

If you prefer, Esper is also available on PyPI for easy installation via pip.


3) Structure Guidelines
-----------------------
* Entities 

Entities are simple integer IDs (1, 2, 3, 4, etc.).
They are "created", but they are not used directly. They are simply used as index
IDs in the internal Component database, for all Components that are assigned to
them. Think of them as Component collection IDs.

* Components

Components are defined as simple Python classes. In keeping with a pure Entity System
design philosophy, they should not contain any logic. They might have initialization
code, but no processing logic whatsoever. A simple Component might look like::

    class Position(x=0, y=0)
        self.x = x
        self.y = y

* Processors

Processors, also commonly known as "Systems", are where all processing logic is defined.
All Processors must inherit from the *esper.Processor* class, and have a method called
*process*. Other than that, there are no restrictions. All Processors will have access
to the World instance, to allow easy querying of Components. A simple Processor might look like::

    class MovementProcessor(esper.Processor):
        def __init__(self):
            super().__init__()

        def process(self):
            for ent, (vel, pos) in self.world.get_components(Velocity, Position):
                pos.x += vel.x
                pos.y += vel.y

Here you can see the standard usage of the world.get_components method. This allows
efficient iteration over all Entities that contain both a Velocity and Position
Component. You also get a reference to the Entity ID for the current pair of Velocity/Position
Components if you should need it.


4) Usage
--------
The first step after importing Esper is to create a World instance. A World is the main core
of Esper. It is responsible for creating Entities and assigning Components to them, and handling
running of all assigned Processors.

Create a World instance. You can have a single World for your entire game, or you can have a
eparate instance for each of your game scenes. Whatever makes sense for your design::

    world = esper.World()


Create some Processor instances, and assign them to the World. You can specify an
optional processing priority (higher numbers are processed first). All Processors are
priority "0" by default::

    movement_processor = MovementProcessor()
    rendering_processor = RenderingProcessor()
    world.add_processor(movement_processor)
    world.add_processor(rendering_processor, priority=3)


Create an Entity, and assign some Component instances to it::

    player = world.create_entity()
    world.add_component(player, Velocity(x=0.9, y=1.2))
    world.add_component(player, Position(x=5, y=5))


Running all Processors is done with a single call to world.process(). This will call the
process method on all assigned Processors, in order of their priority (if any)::

    world.process()


Note: You can pass any args you need to *world.process()*, but you must also make sure to recieve
them properly in the *process()* methods of your Processors. For example, if you pass a delta time
argument as *world.process(dt)*, your Processor's *process()* methods should all receive it as:
*process(self, dt)*

5) Examples
-----------

See the **/examples** folder to get some idea of how a game might be structured.