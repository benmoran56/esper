Esper
=====
**Esper is a lightweight Entity System for Python, with a focus on performance.**

The design is based on the Entity System concepts described by Adam Martin in his blog at
T-Machines.org, and others.

Esper is inspired by Sean Fisk's **ecs** https://github.com/seanfisk/ecs,
and Marcus von Appen's **ebs** https://bitbucket.org/marcusva/python-utils.


1) Compatibility
----------------
Esper is developed for Python 3, and is also know to work on Pypy3. Being written in pure
Python, it should work on any compliant interpreter. Python 2, however, is not supported
due to differences in dictionary key iteration. It could be made to work with a little
effort, but official support is not planned.


2) Installation
---------------
No installation is necessary. This is tiny library with no dependencies. Simply copy
the *esper* directory into the top level of your project folder, and *import esper*.


3) Structure Guidelines
-----------------------
* Entities 

Entities are simple integer IDs which contain no code or logic whatsover in Esper.
They are "created", but they are not used directly. Merely, they are used as index
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
to the World instance, to allow easy querying of Components. Many Processors will have
an __init__() method to keep some state, but it's not strictly necessary. A simple
Processor might look like::

    class MovementProcessor:
        def process(self):
            for ent, (vel, pos) in self.world.get_components(Velocity, Position):
                pos.x += vel.x
                pos.y += vel.y

Here you can see the standard usage of the world.get_components method. This allows
efficient iteration over all Entities that contain both a Velocity and Position
component.


4) Usage
--------
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
and assign Component instances to it::

    player = world.create_entity()
    world.add_component(player, Velocity(x=0.9, y=1.2))
    world.add_component(player, Position(x=5, y=5))
    
Processing everything is done with a single call to world.process(). This will call the 
process method on all assigned Processors, in order of their priority (if any)::

    world.process()


5) API Guide
------------

**COMING SOON**
