esper - API documentation
=========================

Processors
----------
 .. autoclass:: esper.Processor


Components
----------
**esper** does not define any specific Component base class
to inherit from. Any valid Python class can be used. For more
compact definitions, the ``@dataclass`` decorator from the
``dataclasses`` module is quite useful. You can also use a
``namedtuple`` instead of a class, but this is limited to
cases where the Component's data does not need to be modified.
Three examples of valid Components::

    class Velocity:
        def __init__(self, x=0.0, y=0.0, accel=0.1, decel=0.75, maximum=3):
            self.vector = Vec2(x, y)
            self.accel = accel
            self.decel = decel
            self.maximum = maximum


    @dataclass
    class Camera:
        current_x_offset:   float = 0
        current_y_offset:   float = 0


    Interaction = namedtuple('Interaction', 'interaction_type target_name')


The World context
-----------------

.. autofunction:: esper.switch_world
.. autofunction:: esper.delete_world
.. autofunction:: esper.list_worlds
.. autofunction:: esper.create_entity
.. autofunction:: esper.delete_entity
.. autofunction:: esper.entity_exists
.. autofunction:: esper.add_processor
.. autofunction:: esper.remove_processor
.. autofunction:: esper.get_processor
.. autofunction:: esper.component_for_entity
.. autofunction:: esper.components_for_entity
.. autofunction:: esper.add_component
.. autofunction:: esper.remove_component
.. autofunction:: esper.try_remove_component
.. autofunction:: esper.get_component
.. autofunction:: esper.get_components
.. autofunction:: esper.has_component
.. autofunction:: esper.has_components
.. autofunction:: esper.try_component
.. autofunction:: esper.try_components
.. autofunction:: esper.process
.. autofunction:: esper.timed_process
.. autofunction:: esper.clear_database
.. autofunction:: esper.clear_cache
.. autofunction:: esper.clear_dead_entities

Events
------
For convenience, **esper** includes functionality for
dispatching and handling events. This is limited in scope,
but should be robust enough for most general use cases.

.. autofunction:: esper.dispatch_event
.. autofunction:: esper.set_handler
.. autofunction:: esper.remove_handler
