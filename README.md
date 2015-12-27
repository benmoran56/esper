Esper
=====
**Esper is a lightweight Entity System for Python, designed with a focus on performance.**

The design is based on the Entity System concepts described by Adam Martin in his blog at
T-Machines.org, and others.

Esper takes inspiration by Sean Fisk's **ecs** https://github.com/seanfisk/ecs,
and Marcus von Appen's **ebs** https://bitbucket.org/marcusva/python-utils.


Compatibility
-------------
Esper is developed for Python 3, and is also know to work on Pypy3.
Python 2 is not supported, due to differences in dictionary key iteration. It can be
made to work with a little effort, but official support is not planned.


Installation
------------
Esper is a tiny library, and is intended to be dropped directly into your project.
Simply copy the *esper* directory into the top level of your project folder, and
*import esper*.


Usage
-----

The first step is to create a World instance. A World is the main core of Esper.
It is responsible for creating Entities and tracking their Component relationships.
It also runs all assigned Processors. 

Create a World instance::

    world = esper.World()

Create some Processor instances, and assign them to the World. You can specify an
optional processing priority (higher number is lower priority). All Processors are
priority "0" by default::

    movement_processor = MovementProcessor()
    rendering_processor = RenderingProcessor()
    world.add_processor(processor_instance=movement_processor)
    world.add_processor(processor_instance=rendering_processor, priority=3)

Entities are simply integer IDs, which track groups of Components. Create an Entity,
and assign Components to it:: 

    player = world.create_entity()
    world.add_component(player, Velocity(x=0.9, y=1.2))
    world.add_component(player, Position(x=5, y=5))

