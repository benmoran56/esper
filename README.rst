.. image:: https://travis-ci.org/benmoran56/esper.svg?branch=master
    :target: https://travis-ci.org/benmoran56/esper

Esper
=====
**Esper is a lightweight Entity System for Python, with a focus on performance.**

Esper is an MIT licensed Entity System, or, Entity Component System (ECS).
The design is based on the Entity System concepts outlined by Adam Martin in his blog at
T-Machines.org, and others. Efforts were made to keep it as lightweight and performant as possible.

There is a fairly accurate writeup of what Entity Systems are in this Wikipedia article:
https://en.wikipedia.org/wiki/Entity_component_system

Inspired by Sean Fisk's **ecs** https://github.com/seanfisk/ecs,
and Marcus von Appen's **ebs** https://bitbucket.org/marcusva/python-utils.


What's New
----------
**0.9.7** - By default, entities are now lazily deleted. When calling *World.delete_entity(entity_id)*,
            Entities are now placed into a queue to be deleted at the beginning of the next call
            to World.process(). This means it is now safe to delete entities even while iterating
            over components in your processors. This should allow for cleaner Processor classes, by
            removing the need to manually track and delete "dead" Entities after iteration. If you
            do wish to delete an Entity immediately, simply pass the new optional *immediate=True*
            argument. Ie: *self.world.delete_entity(entity, immediate=True)*.

**0.9.6** - A new method has been added: *World.get_processor* which returns a *Processor*
            instance by type. This could be useful if you wish to call a specific method
            from another *Processor* from within a *Processor*. For example:
            *self.world.get_processor(OtherProcessorType).some_method()*

**0.9.5** - A new method was added: *World.components_for_entity* which returns a tuple of all
            *Components* that are assigned to an *Entity*. This is probably not useful within
            standard *Processor* logic, but could be useful for serializing a specific *Entity's*
            state. For example: saving player status to disk, or passing to another scene in your
            game that might have a separate *World*. You can recreate the *Entity* using these
            exported *Component* instances.
            In addition to the new method, the behavior of the *World.component_for_entity* method
            has changed slightly. It will not raise a *KeyError* if the *Entity* ID doesn't exist,
            instead of passing silently.

**0.9.4** - A new method was added: *World.has_component* which returns a Boolean (True/False).
            This is mostly a simple convenience method to make writing some types of logic in
            *Processors*.  This release also has a bit better test coverage, including coverage
            for the undocumented *esper.CachedWorld*. As the name implies, this is a alternate
            *World* that uses the *functools.lru_cache* module from the Python standard library.
            Feel free to try this out in your program, or run the benchmark in the examples folder.
            The API is the same, and it should be faster than the standard *World* in most cases. 
            After more testing/feedback, it should be documented in a future release.
            Thanks to Christopher Arndt for his work on this. 


1) Compatibility
----------------
Esper is developed for Python 3. It will also work on Pypy3. Being written in pure
Python, it should work on any compliant interpreter. Current automated testing is done
for both CPython and PyPy. Python 2 is not supported in the main branch,
but Christopher Arndt is currently maintaining a branch here:
https://github.com/SpotlightKid/esper/tree/python2


2) Installation
---------------
No installation is necessary. Esper is a tiny library with no dependencies. Simply copy
the *esper* directory into the top level of your project folder, and *import esper*.

If you prefer, Esper is also available on PyPI for easy installation via pip.


3) Project Structure
--------------------
* World

A World is the main point of interaction in Esper. After creating a World object, you will use
that object to create Entities and assigning Components to them. A World is also assigned all of
your Processor instances, and handles smoothly running everything with a single call per frame.
Of course, Entities, Components and Processors can be created and assigned, or deleted while
your application is running.


* Entities 

Entities are simple integer IDs (1, 2, 3, 4, etc.).
Entities are "created", but they are generally not used directly. Instead, they are
simply used as IDs in the internal Component database, to track collections of Components.
Creating an Entity is done with the World.create_entity() method.


* Components

Components are defined as simple Python classes. In keeping with a pure Entity System
design philosophy, they should not contain any logic. They might have initialization
code, but no processing logic whatsoever. A simple Component might look like::

    class Position:
        def __init__(self, x=0.0, y=0.0):
            self.x = x
            self.y = y


* Processors

Processors, also commonly known as "Systems", are where all processing logic is defined and executed.
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

In the above code, you can see the standard usage of the *World.get_components()* method. This method
allows efficient iteration over all Entities that contain the specified Component types. You also
get a reference to the Entity ID for the current pair of Velocity/Position Components, in case you
should need it. For example, you may have a Processor that will delete certain Entites. You could
add these Entity IDs to a list, and call the *self.world.delete_entity()* method on them after
you're done iterating over the Components.


4) Usage
--------
The first step after importing Esper is to create a World instance. You can have a single World
instance for your entire game, or you can have a separate instance for each of your game scenes.
Whatever makes sense for your design. Create a World instance like this::

    world = esper.World()


Create some Processor instances, and assign them to the World. You can specify an
optional processing priority (higher numbers are processed first). All Processors are
priority "0" by default::

    movement_processor = MovementProcessor()
    collision_processor = CollisionProcessor()
    rendering_processor = RenderingProcessor()
    world.add_processor(movement_processor, priority=2)
    world.add_processor(collision_processor, priority=3)
    world.add_processor(rendering_processor)


Create an Entity, and assign some Component instances to it::

    player = world.create_entity()
    world.add_component(player, Velocity(x=0.9, y=1.2))
    world.add_component(player, Position(x=5, y=5))

Optionally, Component instances can be assigned directly to the Entity on creation::

    player = world.create_entity(
        Velocity(x=0.9, y=1.2),
        Position(x=5, y=5)
    )


Running all Processors is done with a single call to world.process(). This will call the
process method on all assigned Processors, in order of their priority::

    world.process()


Note: You can pass any args you need to *world.process()*, but you must also make sure to recieve
them properly in the *process()* methods of your Processors. For example, if you pass a delta time
argument as *world.process(dt)*, your Processor's *process()* methods should all receive it as:
*def process(self, dt):*

* Additional Methods

Have a look through *esper/world.py* for an idea of what additional functionality is available. All
methods have docstrings with details on usage, which will be put into a real API document at some point.
Here is a quick list of the methods, whose names should be semi-explanitory::


    World.create_entity()
    World.delete_entity(entity)
    World.add_processor(processor_instance)
    World.remove_processor(ProcessorType)
    World.add_component(entity, component_instance)
    World.remove_component(entity, ComponentType)
    World.get_component(ComponentType)
    World.get_components(ComponentTypeA, ComponentTypeB, Etc)
    World.component_for_entity(entity, ComponentType)
    World.components_for_entity(entity)
    World.has_component(entity, ComponentType)
    World.process()

5) Examples
-----------

See the **/examples** folder to get an idea of how the basic structure of a game looks.