[![pypi](https://badge.fury.io/py/esper.svg)](https://pypi.python.org/pypi/esper)
[![rtd](https://readthedocs.org/projects/esper/badge/?version=latest)](https://esper.readthedocs.io)
[![PyTest](https://github.com/benmoran56/esper/actions/workflows/unit-tests.yml/badge.svg)](https://github.com/benmoran56/esper/actions/workflows/unit-tests.yml)

esper is a lightweight Entity System module for Python, with a focus on performance
===================================================================================

**esper** is an MIT licensed Entity System, or, Entity Component System (ECS).
The design is based on the Entity System concepts originally popularized by
Adam Martin and others. The primary focus for **esper** is to maximize perfomance,
while handling most common use cases. 

For more information on the ECS pattern, you might find the following
resources interesting:
https://github.com/SanderMertens/ecs-faq/blob/master/README.md
https://github.com/jslee02/awesome-entity-component-system/blob/master/README.md
https://en.wikipedia.org/wiki/Entity_component_system

API documentation is hosted at ReadTheDocs: https://esper.readthedocs.io
Due to the small size of the project, this README currently serves as general usage
documentation.

> :warning: **esper 3.0 introduces breaking changes**. Version 3.0 removes the
> World object, and migrates its methods to module level functions. Multiple 
> contexts can be created and switched between. The v2.x README can be found
> here: https://github.com/benmoran56/esper/blob/v2_maintenance/README.md

- [Compatibility](#compatibility)
- [Installation](#installation)
- [Design](#design)
- [Quick Start](#quick-start)
- [General Usage](#general-usage)
  * [Adding and Removing Processors](#adding-and-removing-processors)
  * [Adding and Removing Components](#adding-and-removing-components)
  * [Querying Specific Components](#querying-specific-components)
  * [Boolean and Conditional Checks](#boolean-and-conditional-checks)
  * [More Examples](#more-examples)
- [Event Dispatching](#event-dispatching)
- [Contributing](#contributing)


Compatibility
=============
**esper** attempts to target all currently supported Python releases (any Python version that is
not EOL). **esper** is written in 100% pure Python, so *any* compliant interpreter should work.
Automated testing is currently done for both CPython and PyPy3.


Installation
============
**esper** is a pure Python package with no dependencies, so installation is flexible.
You can simply copy the `esper` folder right into your project, and `import esper`.
You can also install into your site-packages from PyPi via `pip`::

    pip install --user --upgrade esper

Or from the source directory::

    pip install . --user


Design
======

* World Context

**esper** uses the concept of "World" contexts. When you first `import esper`, a default context is
active. You create Entities, assign Components, register Processors, etc., by calling functions
on the `esper` module. Entities, Components and Processors can be created, assigned, or deleted
while your game is running. A simple call to `esper.process()` is all that's needed for each
iteration of your game loop. Advanced users can switch contexts, which can be useful for
isolating different game scenes that have different Processor requirements.


* Entities 

Entities are defined internally as plain integer IDs (1, 2, 3, 4, etc.). Generally speaking
you should not need to care about the individual entity IDs, since entities are queried based
on their specific combination of Components - not by their ID. An Entity can be thought of as
a specific combination of Components. Creating an Entity is done with the `esper.create_entity()`
function. You can pass Component instances on creation or add/remove them later.

* Components

Components are defined as simple Python classes. In keeping with a pure Entity System design
philosophy, Components should not contain any processing logic. They may contain initialization
logic, and you can take advantage of Python language features, like properties, to simplify data
lookup. The key point is that game logic does not belong in these classes, and Components should
have no knowledge of other Components or Entities. A simple Component can be defined as::

    class Position:
        def __init__(self, x=0.0, y=0.0):
            self.x = x
            self.y = y

To save on typing, the standard library dataclass decorator is quite useful. 
https://docs.python.org/3/library/dataclasses.html#module-dataclasses
This decorator simplifies defining your Component classes. The attribute names don't need to
be repeated, and you can still instantiate the Component with positional or keyword arguments::

    from dataclasses import dataclass as component

    @component
    class Position:
        x: float = 0.0
        y: float = 0.0

Python language features, like properties, can be useful to simplify data access. For example,
a Body component that is often repositioned may benefit from a local AABB (axis aligned bounding
box) property::

    @dataclass
    class Body:
        width:  int
        height: int
        pos_x:  float = 0
        pos_y:  float = 0

        @property
        def aabb(self) -> tuple[float, float, float, float]:
            return self.pos_x, self.pos_y, self.pos_x + self.width, self.pos_y + self.height


* Processors

Processors, also commonly known as "Systems", are where all processing logic is defined and executed.
All Processors must inherit from the `esper.Processor` class, and have a method called `process`.
Other than that, there are no restrictions. You can define any additional methods you might need. 
A simple Processor might look like::

    class MovementProcessor(esper.Processor):

        def process(self):
            for ent, (vel, pos) in esper.get_components(Velocity, Position):
                pos.x += vel.x
                pos.y += vel.y

In the above code, you can see the standard usage of the `esper.get_components()` function. This
function allows efficient iteration over all Entities that contain the specified Component types.
This function can be used for querying two or more components at once. Note that tuple unpacking
is necessary for the return component pairs: `(vel, pos)`.  In addition to Components, you also
get a reference to the Entity ID for the current pair of Velocity/Position Components. This entity
ID can be useful in a variety of cases. For example, if your Processor will need to delete certain
Entites, you can call the `esper.delete_entity()` function on this Entity ID. Another common use
is if you wish to add or remove a Component on this Entity as a result of some condition being met. 
For example, an Entity that should be deleted once it's `Lifecycle` Component reaches 0::

    class LifecycleProcessor(esper.Processor):
        def __init__(self, ...):
            ...
    
        def process(self, dt):
            for ent, (life, rend) in esper.get_components(Lifecycle, Renderable):
                life.lifespan -= dt
                if life.lifespan <= 0:
                    esper.delete_entity(ent)


Quick Start
===========

To get started, simply import **esper**::

    import esper

From there, define some Components, and create Entities that use them::

    player = esper.create_entity()
    esper.add_component(player, Velocity(x=0.9, y=1.2))
    esper.add_component(player, Position(x=5, y=5))

Optionally, Component instances can be assigned directly to the Entity on creation::

    player = esper.create_entity(Velocity(x=0.9, y=1.2), Position(x=5, y=5))


Design some Processors that operate on these Component types, and then register them with
**esper** for processing. You can specify an optional priority (higher numbers are processed first).
All Processors are priority "0" by default::

    movement_processor = MovementProcessor()
    collision_processor = CollisionProcessor()
    rendering_processor = RenderingProcessor()
    esper.add_processor(collision_processor, priority=2)
    esper.add_processor(movement_processor, priority=3)
    esper.add_processor(rendering_processor)
    # or just add them in one line: 
    esper.add_processor(SomeProcessor())


Executing all Processors is done with a single call to `esper.process()`. This will call the
`process` method on all assigned Processors, in order of their priority. This is usually called
once per frame update of your game (every tick of the clock).::

    esper.process()


**Note:** You can pass any arguments (or keyword arguments) you need to `esper.process()`, but you
must also make sure to receive them properly in the `process()` methods of your Processors. For
example, if you pass a delta time argument as `esper.process(dt)`, your Processor's `process()`
methods should all receive it as: `def process(self, dt):`
This is appropriate for libraries such as **pyglet**, which automatically pass a delta time value
into scheduled functions.  


General Usage
=============

World Contexts
--------------
**esper** has the capability of supporting multiple "World" contexts. On import, a "default" World is
active. All creation of Entities, assignment of Processors, and all other operations occur within
the confines of the active World. In other words, the World contexts are completely isolated from
each other. For basic games and designs, you may not need to bother with this functionality. A
single default World context can often be enough. For advanced use cases, such as when different
scenes in your game have different Entities and Processor requirements, this functionality can be
quite useful. World context operations are done with the following functions::
* esper.list_worlds()
* esper.switch_world(name)
* esper.delete_world(name)

When switching Worlds, be mindful of the `name`. If a World doesn't exist, it will be created when
you first switch to it. You can delete old Worlds if they are no longer needed, but you can not
delete the currently active World.  

Adding and Removing Processors
------------------------------
You have already seen examples of adding Processors in an earlier section. There is also a
`remove_processor` function available:

* esper.add_processor(processor_instance)
* esper.remove_processor(ProcessorClass)

Depending on the structure of your game, you may want to add or remove certain Processors when changing
scenes, etc. 

Adding and Removing Components
------------------------------
In addition to adding Components to Entities when you're creating them, it's a common pattern to add or
remove Components inside your Processors. The following functions are available for this purpose: 

* esper.add_component(entity_id, component_instance)
* esper.remove_component(entity_id, ComponentClass)

As an example of this, you could have a "Blink" component with a `duration` attribute. This can be used
to make certain things blink for a specific period of time, then disappear. For example, the code below
shows a simplified case of adding this Component to an Entity when it takes damage in one processor. A 
dedicated `BlinkProcessor` handles the effect, and then removes the Component after the duration expires::

    class BlinkComponent:
        def __init__(self, duration):
            self.duration = duration


    .....


    class CollisionProcessor(esper.Processor):

        def process(self, dt):
            for ent, enemy in esper.get_component(Enemy):
                ...
                is_damaged = self._some_method()
                if is_damaged:
                    esper.add_component(ent, BlinkComponent(duration=1))
                ...


    class BlinkProcessor(esper.Processor):

        def process(self, dt):
            for ent, (rend, blink) in esper.get_components(Renderable, BlinkComponent):
                if blink.duration < 0:
                    # Times up. Remove the Component:
                    rend.sprite.visible = True
                    esper.remove_component(ent, BlinkComponent)
                else:
                    blink.duration -= dt
                    # Toggle between visible and not visible each frame:
                    rend.sprite.visible = not rend.sprite.visible


Querying Specific Components
----------------------------
If you have an Entity ID and wish to query one specific, or ALL Components that are assigned
to it, the following functions are available: 

* esper.component_for_entity
* esper.components_for_entity

The `component_for_entity` function is useful in a limited number of cases where you know a specific
Entity ID, and wish to get a specific Component for it. An error is raised if the Component does not
exist for the Entity ID, so it may be more useful when combined with the `has_component`
function that is explained in the next section. For example::

    if esper.has_component(ent, SFX):
        sfx = esper.component_for_entity(ent, SFX)
        sfx.play()

The `components_for_entity` function is a special function that returns ALL the Components that are
assigned to a specific Entity, as a tuple. This is a heavy operation, and not something you would
want to do each frame or inside your `Processor.process` method. It can be useful, however, if
you wanted to transfer all of a specific Entity's Components between two separate contexts
(such as when changing Scenes, or levels). For example::
    
    player_components = esper.components_for_entity(player_entity_id)
    esper.switch_world('context_name')
    player_entity_id = esper.create_entity(player_components)

Boolean and Conditional Checks
------------------------------
In some cases you may wish to check if an Entity has a specific Component before performing
some action. The following functions are available for this task:

* esper.has_component(entity, ComponentType)
* esper.has_components(entity, ComponentTypeA, ComponentTypeB)
* esper.try_component(entity, ComponentType)
* esper.try_components(entity, ComponentTypeA, ComponentTypeB)


For example, you may want projectiles (and only projectiles) to disappear when hitting a wall in
your game. We can do this by checking if the Entity has a `Projectile` Component. We don't  want
to do anything to this Component, simply check if it's there. Consider this example::

    class CollisionProcessor(esper.Processor):

        def process(self, dt):
            for ent, body in esper.get_component(PhysicsBody):
                ...
                colliding_with_wall = self._some_method(body):
                if colliding_with_wall and esper.has_component(ent, Projectile):
                    esper.delete_entity(ent)
                ...


In a different scenario, we may want to perform some action on an Entity's Component, *if* it has
one. For example, a MovementProcessor that skips over Entities that have a `Stun` Component::

    class MovementProcessor(esper.Processor):

        def process(self, dt):
            for ent, (body, vel) in esper.get_components(PhysicsBody, Velocity):

                if esper.has_component(ent, Stun):
                    stun = esper.component_for_entity(ent, Stun)
                    stun.duration -= dt
                    if stun.duration <= 0:
                        esper.remove_component(ent, Stun)
                    continue    # Continue to the next Entity

                movement_code_here()
                ...


Let's look at the core part of the code::

    if esper.has_component(ent, Stun):
        stun = esper.component_for_entity(ent, Stun)
        stun.duration -= dt

This code works fine, but the `try_component` function can accomplish the same thing with one
less function call. The following example will get a specific Component if it exists, or
return None if it does not::

    stun = esper.try_component(ent, Stun)
    if stun:
        stun.duration -= dt

With Python 3.8+, the new "walrus" operator (`:=`) can also be used, making the `try_component`
functions even more concise ::

    if stun :=  esper.try_component(ent, Stun):
        stun.duration -= dt


More Examples
-------------

See the `/examples` folder to get an idea of how the basic structure of a game might look.

Event Dispatching
=================

**esper** includes basic support for event dispatching and handling. This functionality is
provided by three functions to set (register), remove, and dispatch events. Minimal error
checking is done, so it's left up to the user to ensure correct naming and number of
arguments are used when dispatching and receiving events.

Events are dispatched by name::

    esper.dispatch_event('event_name', arg1, arg2)

In order to receive the above event, you must register handlers. An event handler can be a
function or class method. Registering a handler is also done by name::

    esper.set_handler('event_name', my_func)
    # or
    esper.set_handler('event_name', self.my_method)

**Note:** Only weak-references are kept to the registered handlers. If a handler is garbage
collected, it will be automatically un-registered by an internal callback.

Handlers can also be removed at any time, if you no longer want them to receive events::

    esper.remove_handler('event_name', my_func)
    # or
    esper.remove_handler('event_name', self.my_method)

Registered events and handlers are part of the current `World` context. 

Contributing
============

Contributions to **esper** are always welcome, but there are some specific project goals to keep in mind:

- Pure Python code only: no binary extensions, Cython, etc.
- Try to target all non-EOL Python versions. Exceptions can be made if there is a compelling reason.
- Avoid bloat as much as possible. New features will be considered if they are commonly useful. Generally speaking, we don't want to add functionality that is better served by another module or library. 
- Performance is preferrable to readability. The public API should remain clean, but ugly internal code is acceptable if it provides a performance benefit. Every cycle counts! 

If you have any questions before contributing, feel free to [open an issue].

[open an issue]: https://github.com/benmoran56/esper/issues
