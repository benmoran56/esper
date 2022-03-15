esper - API documentation
=========================

Processors
----------
 .. autoclass:: esper.Processor


Components
----------
**esper** does not define any specific
Component base class. Instead, normal
Python classes are used as Components.


The World Class
---------------
 .. autoclass:: esper.World
    :members:


Events
------
**esper** provides basic functionality for
dispatching and handling events. Minimal
error checking is done. It's left up to the
user to ensure that events and handlers are
dispatched and received with the correct
number of arguments.

.. autofunction:: esper.dispatch_event
.. autofunction:: esper.set_handler
.. autofunction:: esper.remove_handler
