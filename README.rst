.. image:: https://travis-ci.org/benmoran56/esper.svg?branch=master
    :target: https://travis-ci.org/benmoran56/esper

.. image:: https://readthedocs.org/projects/esper/badge/?version=latest
    :target: https://esper.readthedocs.io


Esper
=====
**Esper is a lightweight Entity System for Python, with a focus on performance.**

Esper is an MIT licensed Entity System, or, Entity Component System (ECS).
The design is based on the Entity System concepts outlined by Adam Martin in his blog at
http://t-machine.org/, and others. Efforts were made to keep it as lightweight and performant
as possible.

There is a fairly accurate writeup describing Entity Systems in this Wikipedia article:
https://en.wikipedia.org/wiki/Entity_component_system

API documentation is hosted at ReadTheDocs: https://esper.readthedocs.io

Inspired by Sean Fisk's **ecs** https://github.com/seanfisk/ecs,
and Marcus von Appen's **ebs** https://bitbucket.org/marcusva/python-utils.


What's New
----------
**1.2** - Calls to `super()` are no longer necessary in your Processor subclasses.
            This should eliminate a fair amount of boilerplate. The README has also been updated
            with more usage examples. All methods should now have at least one example. And finally,
            wheels are now uploaded to PyPi. This should help with packaging systems that only support
            wheels. Addresses issue #38.

**1.0.0** - Esper is now using simple lru_caching internally by default. The cache is currently
            flushed when adding or deleting Entities or Components from the World, Component queries
            are much faster otherwise. This will likely be improved in a Future version. In addition
            to caching, Esper now supports passing kwargs to Processors. Continuous Integration testing
            is now being done for Python 3.7.

**0.9.9** - The big change in this release is that esper has been condensed into a single
            file: `esper.py`. This will make it simple to just drop into your project folder,
            without cluttering your project with additional folders that didn't really need to
            exist. You can still install it from PyPi via pip if you wish, but it's easy enough
            to just ship with your project (and of course the license allows for this).

**0.9.8** - This release contains a new timer that can be enabled to profile Processor execution
            time. Simply pass the "timed=True" parameter to the World on instantiation, and a new
            World.process_times dictionary will be available. This contains the total execution time
            of each Processor in milliseconds, and can be logged, printed, or displayed on screen as
            is useful. It's useful to see a quick profile of which processors are using the most cpu
            time, without fully profiling your game. This release also contains some consolidations
            and cleanups for the benchmarks.

**0.9.7** - By default, entities are now lazily deleted. When calling *World.delete_entity(entity_id)*,
            Entities are now placed into a queue to be deleted at the beginning of the next call
            to World.process(). This means it is now safe to delete entities even while iterating
            over components in your processors. This should allow for cleaner Processor classes, by
            removing the need to manually track and delete "dead" Entities after iteration. If you
            do wish to delete an Entity immediately, simply pass the new optional *immediate=True*
            argument. Ie: *self.world.delete_entity(entity, immediate=True)*.


1) Compatibility
----------------
Esper is a Python 3 library only. Specifically, all currently supported versions of Python 3. 
It also supports Pypy3. Being written in pure Python, it should work on *any* compliant
interpreter. Continuous Integration (automated testing) is done for both CPython and PyPy3.


2) Installation
---------------
No installation is necessary. Esper is a tiny library with no dependencies. Simply copy
*esper.py* into the top level of your project folder, and *import esper*.

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
All Processors must inherit from the *esper.Processor* class, and have a method called *process*.
Other than that, there are no restrictions. All Processors will have access to the World instance,
which is how you query Components to operate on. A simple Processor might look like::

    class MovementProcessor(esper.Processor):

        def process(self):
            for ent, (vel, pos) in self.world.get_components(Velocity, Position):
                pos.x += vel.x
                pos.y += vel.y

In the above code, you can see the standard usage of the *World.get_components()* method. This
method allows efficient iteration over all Entities that contain the specified Component types.
This method can be used for querying two or more components at once. Note that tuple unpacking
is necessary for the return component pairs: *(vel, pos)*.  In addition the Components, you also
get a reference to the Entity ID (the *ent* object) for the current pair of Velocity/Position
Components. This entity ID can be useful in a variety of cases. For example, if your Processor
will need to delete certain Entites, you can call the *self.world.delete_entity()* method on
this Entity ID. Another common use is if you wish to add or remove a Component on this Entity
as a result of some condition being met. 


4) Basic Usage
--------------

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
    # or just add them in one line: 
    world.add_processor(SomeProcessor())


Create an Entity, and assign some Component instances to it::

    player = world.create_entity()
    world.add_component(player, Velocity(x=0.9, y=1.2))
    world.add_component(player, Position(x=5, y=5))

Optionally, Component instances can be assigned directly to the Entity on creation::

    player = world.create_entity(Velocity(x=0.9, y=1.2),
                                 Position(x=5, y=5))


Executing all Processors is done with a single call to world.process(). This will call the
process method on all assigned Processors, in order of their priority. This is usually called
once per frame update of your game.::

    world.process()


Note: You can pass any args you need to *world.process()*, but you must also make sure to recieve
them properly in the *process()* methods of your Processors. For example, if you pass a delta time
argument as *world.process(dt)*, your Processor's *process()* methods should all receive it as:
*def process(self, dt):*
This is appropriate for libraries such as **pyglet**, which automatically pass a delta time value
into scheduled methods.  


5) Additional methods
=====================

Adding and Removing Processors
------------------------------
You have already seen examples of adding Processors in an eariler section. There is also a *remove_processor*
method available:

* World.add_processor(processor_instance)
* World.remove_processor(ProcessorClass)

Depending on the structure of your game, you may want to add or remove certain Processors when changing
scenes, etc. 

Adding and Removing Components
------------------------------
In addition to adding Components to Entities when you're creating them, it's a common pattern to add or
remove Components inside of your Processors. The following methods are availble for this purpose: 

* World.add_component(entity_id, component_instance)
* World.remove_component(entity_id, ComponentClass)

As an example of this, you could have a "Blink" component with a *duration* attribute. This can be used
to make certain things blink for s specific period of time, then dissapear. For example, the code below
shows a simplified case of adding this Component to an Entity when it takes damage in one processor. A 
dedicated *BlinkProcessor* handles the effect, and then removes the Component after the duration expires::

    class BlinkComponent:
        def __init__(self, duration):
            self.duration = duration


    .....


    class CollisionProcessor(esper.Processor):

        def process(self, dt):
            for ent, enemy in self.world.get_component(Enemy):
                ...
                is_damaged = self._some_method()
                if is_damaged:
                    self.world.add_component(ent, BlinkComponent(duration=1))
                ...


    class BlinkProcessor(esper.Processor):

        def process(self, dt):
            for ent, (rend, blink) in self.world.get_components(Renderable, BlinkComponent):
                if blink.duration < 0:
                    # Times up. Remove the Component:
                    rend.sprite.visible = True
                    self.world.remove_component(ent, BlinkComponent)
                else:
                    blink.duration -= dt
                    # Toggle between visible and not visible each frame:
                    rend.sprite.visible = not rend.sprite.visible


Querying Specific Components
----------------------------
If you have an Engity ID and wish to query one specific, or ALL Components that are assigned
to it, the following methods are available: 

* World.component_for_entity
* World.components_for_entity

The *component_for_entity* method is useful in a limited number of cases where you know a specific
Entity ID, and wish to get a specific Component for it. An error is raised if the Component does not
exist for the Entity ID, so it may be more useful when combined with the *has_component*
method that is explained in the next section. For example::

    if self.world.has_component(ent, SFX):
        sfx = self.world.component_for_entity(ent, SFX)
        sfx.play()

The *components_for_entity* method is a special method that returns ALL of the Components that are
assigned to a specific Entity, as a tuple. This is a heavy operation, and not something you would
want to do each frame or inside of your *Processor.process* method. It can be useful, however, if
you wanted to transfer all of a specific Entity's Components between two separate World instances
(such as when changing Scenes, or Levels). For example::
    
    player_components = old_world.components_for_entity(player_entity_id)
    ...
    player_entity_id = new_world.create_entity(player_components)

Boolean and Conditional Checks
------------------------------
In some cases you may wish to check if an Entity has a specific Component before performing
some action. The following two methods are available for this task:

* World.has_component(entity, ComponentType)
* World.try_component(entity, ComponentType)

For example, you may want projectiles (and only projectiles) to dissapear when hitting a 
wall in your game. The simplified code below shows how that might look::

    class CollisionProcessor(esper.Processor):

        def process(self, dt):
            for ent, body in self.world.get_component(PhysicsBody):
                ...
                colliding_with_wall = self._some_method(body):
                if colliding_with_wall and self.world.has_component(ent, Projectile):
                    self.world.delete_entity(ent)
                ...

The above example is easy enough, as you don't want to actually do anything to the Component - 
just check if it's there. In cases where you want to both check if a Component exists, and then
operate on it if so, the *try_component* method is useful. Consider the following example, where
you want to first check if an Entity has a Component, get it if so, then operate on it. You could
write it this way:: 

    if self.world.has_component(ent, Stun):
        stun = self.world.get_component(ent, Stun)
        stun.duration -= dt

The above code works fine, but the *try_component* method is more concise and slightly faster. 
It allows you to get specific Components only if they exist, but passes silently if they do not::

    for stun in self.world.try_component(ent, Stun):
        stun.duration -= dt


5) More Examples
----------------

See the **/examples** folder to get an idea of how a basic structure of a game might look.
