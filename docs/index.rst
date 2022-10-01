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


The World Class
---------------
 .. autoclass:: esper.World
    :members:


Events
------
For convenience, **esper** includes functionality for
dispatching and handling events. This is limited in scope,
but should be robust enough for most general use cases.

.. autofunction:: esper.dispatch_event
.. autofunction:: esper.set_handler
.. autofunction:: esper.remove_handler
