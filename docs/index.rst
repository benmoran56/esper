esper - API documentation
=========================

Processors
----------
 .. autoclass:: esper.Processor


Components
----------
**esper** does not define any specific Component base class
to inherit from. Instead, a normal Python class can be used.
Also, while it's not required, the the `@dataclass` decorator
from the `dataclasses` module can be useful to help write
compact Component classes.


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
