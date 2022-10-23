import time as _time

from types import MethodType as _MethodType

from typing import Iterable as _Iterable
from typing import List as _List
from typing import Optional as _Optional
from typing import Tuple as _Tuple
from typing import Type as _Type
from typing import TypeVar as _TypeVar

from weakref import ref as _ref
from weakref import WeakMethod as _WeakMethod


version = '2.4'


###################
#  Event system
###################

event_registry: dict = {}


def dispatch_event(name: str, *args) -> None:
    """Dispatch an event by name, with optional arguments.

    Any handlers set with the :py:func:`esper.set_handler` function
    will recieve the event. If no handlers have been set, this
    function call will pass silently.

    :note:: If optional arguments are provided, but set handlers
            do not account for them, it will likely result in a
            TypeError or other undefined crash.
    """
    for func in event_registry.get(name, []):
        func()(*args)


def _make_callback(name: str):
    """Create an internal callback to remove dead handlers."""
    def callback(weak_method):
        event_registry[name].remove(weak_method)
        if not event_registry[name]:
            del event_registry[name]

    return callback


def set_handler(name: str, func) -> None:
    """Register a function to handle the named event type.

    After registering a function (or method), it will receive all
    events that are dispatched by the specified name.

    :note:: Only a weak reference is kept to the passed function,
    """
    if name not in event_registry:
        event_registry[name] = set()

    if isinstance(func, _MethodType):
        event_registry[name].add(_WeakMethod(func, _make_callback(name)))
    else:
        event_registry[name].add(_ref(func, _make_callback(name)))


def remove_handler(name: str, func) -> None:
    """Unregister a handler from receiving events of this name.

    If the passed function/method is not registered to
    receive the named event, or if the named event does
    not exist, this function call will pass silently.
    """
    if func not in event_registry.get(name, []):
        return

    event_registry[name].remove(func)
    if not event_registry[name]:
        del event_registry[name]


###################
#   ECS Classes
###################


_C = _TypeVar('_C')


class Processor:
    """Base class for all Processors to inherit from.

    Processor instances must contain a `process` method, but you are otherwise
    free to define the class any way you wish. Processors should be instantiated,
    and then added to a :py:class:`esper.World` instance by calling
    :py:meth:`esper.World.add_processor`. For example::

        my_world = World()

        my_processor_instance = MyProcessor()
        my_world.add_processor(my_processor_instance)

    After adding your Processors to a :py:class:`esper.World`, Processor.world
    will be set to the World it is in. This allows easy access to the World and
    it's methods from your Processor methods. All Processors in a World will have
    their `process` methods called by a single call to :py:meth:`esper.World.process`,
    so you will generally want to iterate over entities with one (or more) calls to
    the appropriate world methods::

        def process(self):
            for ent, (rend, vel) in self.world.get_components(Renderable, Velocity):
                your_code_here()
    """

    priority = 0
    world: "World"

    def process(self, *args, **kwargs):
        raise NotImplementedError


class World:
    """A World object keeps track of all Entities, Components, and Processors.

    A World contains a database of all Entity/Component assignments. The World
    is also responsible for executing all Processors assigned to it for each
    frame of your game.
    """

    def __init__(self, timed=False):
        self._processors = []
        self._next_entity_id = 0
        self._components = {}
        self._entities = {}
        self._dead_entities = set()

        self._get_component_cache = {}
        self._get_components_cache = {}

        if timed:
            self.process_times = {}
            self._process = self._timed_process

    def clear_cache(self) -> None:
        """Manually clear the internal cache."""
        self._get_component_cache.clear()
        self._get_components_cache.clear()

    def clear_database(self) -> None:
        """Remove all Entities and Components from the World."""
        self._dead_entities.clear()
        self._entities.clear()
        self._components.clear()
        self._next_entity_id = 0
        self.clear_cache()

    def add_processor(self, processor_instance: Processor, priority=0) -> None:
        """Add a Processor instance to the World.

        All processors should subclass :py:class:`esper.Processor`.
        An optional priority argument can be provided. A higher
        priority will be executed first when :py:meth:`esper.World.process`
        is called.
        """
        processor_instance.priority = priority
        processor_instance.world = self
        self._processors.append(processor_instance)
        self._processors.sort(key=lambda proc: proc.priority, reverse=True)

    def remove_processor(self, processor_type: _Type[Processor]) -> None:
        """Remove a Processor from the World, by type.

        Make sure to provide the class itself, **not** an instance. For example::

            # OK:
            self.world.remove_processor(MyProcessor)

            # NG:
            self.world.remove_processor(my_processor_instance)

        """
        for processor in self._processors:
            if type(processor) is processor_type:
                del processor.world
                self._processors.remove(processor)

    def get_processor(self, processor_type: _Type[Processor]) -> _Optional[Processor]:
        """Get a Processor instance, by type.

        This method returns a Processor instance by type. This could be
        useful in certain situations, such as wanting to call a method on a
        Processor, from within another Processor.
        """
        for processor in self._processors:
            if type(processor) is processor_type:
                return processor
        else:
            return None

    def create_entity(self, *components: _C) -> int:
        """Create a new Entity, with optional Components.

        This method returns an Entity ID, which is a plain integer.
        You can optionally pass one or more Component instances to be
        assigned to the Entity on creation. Components can be also be
        added later with the :py:meth:`esper.World.add_component` method.
        """
        self._next_entity_id += 1

        entity = self._next_entity_id

        for component_instance in components:

            component_type = type(component_instance)

            if component_type not in self._components:
                self._components[component_type] = set()

            self._components[component_type].add(entity)

            if entity not in self._entities:
                self._entities[entity] = {}

            self._entities[entity][component_type] = component_instance
            self.clear_cache()

        return entity

    def delete_entity(self, entity: int, immediate: bool = False) -> None:
        """Delete an Entity from the World.

        Delete an Entity and all of it's assigned Component instances from
        the world. By default, Entity deletion is delayed until the next call
        to :py:meth:`esper.World.process`. You can, however, request immediate
        deletion by passing the `immediate=True` parameter. Note that immediate
        deletion may cause issues, such as when done during Entity iteration
        (calls to World.get_component/s).

        Raises a KeyError if the given entity does not exist in the database.
        """
        if immediate:
            for component_type in self._entities[entity]:
                self._components[component_type].discard(entity)

                if not self._components[component_type]:
                    del self._components[component_type]

            del self._entities[entity]
            self.clear_cache()

        else:
            self._dead_entities.add(entity)

    def entity_exists(self, entity: int) -> bool:
        """Check if a specific Entity exists.

        Empty Entities (with no components) and dead Entities (destroyed
        by delete_entity) will not count as existent ones.
        """
        return entity in self._entities and entity not in self._dead_entities

    def component_for_entity(self, entity: int, component_type: _Type[_C]) -> _C:
        """Retrieve a Component instance for a specific Entity.

        Retrieve a Component instance for a specific Entity. In some cases,
        it may be necessary to access a specific Component instance.
        For example: directly modifying a Component to handle user input.

        Raises a KeyError if the given Entity and Component do not exist.
        """
        return self._entities[entity][component_type]

    def components_for_entity(self, entity: int) -> _Tuple[_C, ...]:
        """Retrieve all Components for a specific Entity, as a Tuple.

        Retrieve all Components for a specific Entity. The method is probably
        not appropriate to use in your Processors, but might be useful for
        saving state, or passing specific Components between World instances.
        Unlike most other methods, this returns all the Components as a
        Tuple in one batch, instead of returning a Generator for iteration.

        Raises a KeyError if the given entity does not exist in the database.
        """
        return tuple(self._entities[entity].values())

    def has_component(self, entity: int, component_type: _Type[_C]) -> bool:
        """Check if an Entity has a specific Component type."""
        return component_type in self._entities[entity]

    def has_components(self, entity: int, *component_types: _Type[_C]) -> bool:
        """Check if an Entity has all the specified Component types."""
        return all(comp_type in self._entities[entity] for comp_type in component_types)

    def add_component(self, entity: int, component_instance: _C, type_alias: _Optional[_Type[_C]] = None) -> None:
        """Add a new Component instance to an Entity.

        Add a Component instance to an Entiy. If a Component of the same type
        is already assigned to the Entity, it will be replaced.

        A `type_alias` can also be provided. This can be useful if you're using
        subclasses to organize your Components, but would like to query them
        later by some common parent type.
        """
        component_type = type_alias or type(component_instance)

        if component_type not in self._components:
            self._components[component_type] = set()

        self._components[component_type].add(entity)

        if entity not in self._entities:
            self._entities[entity] = {}

        self._entities[entity][component_type] = component_instance
        self.clear_cache()

    def remove_component(self, entity: int, component_type: _Type[_C]) -> int:
        """Remove a Component instance from an Entity, by type.

        A Component instance can be removed by providing its type.
        For example: world.delete_component(enemy_a, Velocity) will remove
        the Velocity instance from the Entity enemy_a.

        Raises a KeyError if either the given entity or Component type does
        not exist in the database.
        """
        self._components[component_type].discard(entity)

        if not self._components[component_type]:
            del self._components[component_type]

        del self._entities[entity][component_type]

        if not self._entities[entity]:
            del self._entities[entity]

        self.clear_cache()
        return entity

    def _get_component(self, component_type: _Type[_C]) -> _Iterable[_Tuple[int, _C]]:
        entity_db = self._entities

        for entity in self._components.get(component_type, []):
            yield entity, entity_db[entity][component_type]

    def _get_components(self, *component_types: _Type[_C]) -> _Iterable[_Tuple[int, _List[_C]]]:
        entity_db = self._entities
        comp_db = self._components

        try:
            for entity in set.intersection(*[comp_db[ct] for ct in component_types]):
                yield entity, [entity_db[entity][ct] for ct in component_types]
        except KeyError:
            pass

    def get_component(self, component_type: _Type[_C]) -> _List[_Tuple[int, _C]]:
        """Get an iterator for Entity, Component pairs."""
        try:
            return self._get_component_cache[component_type]
        except KeyError:
            return self._get_component_cache.setdefault(
                component_type, list(self._get_component(component_type))
            )

    def get_components(self, *component_types: _Type[_C]) -> _List[_Tuple[int, _List[_C]]]:
        """Get an iterator for Entity and multiple Component sets."""
        try:
            return self._get_components_cache[component_types]
        except KeyError:
            return self._get_components_cache.setdefault(
                component_types, list(self._get_components(*component_types))
            )

    def try_component(self, entity: int, component_type: _Type[_C]) -> _Optional[_C]:
        """Try to get a single component type for an Entity.

        This method will return the requested Component if it exists,
        or None if it does not. This allows a way to access optional Components
        that may or may not exist, without having to first query if the Entity
        has the Component type.
        """
        if component_type in self._entities[entity]:
            return self._entities[entity][component_type]
        return None

    def try_components(self, entity: int, *component_types: _Type[_C]) -> _Optional[_List[_List[_C]]]:
        """Try to get a multiple component types for an Entity.

        This method will return the requested Components if they exist,
        or None if they do not. This allows a way to access optional Components
        that may or may not exist, without first having to query if the Entity
        has the Component types.
        """
        if all(comp_type in self._entities[entity] for comp_type in component_types):
            return [self._entities[entity][comp_type] for comp_type in component_types]
        return None

    def _clear_dead_entities(self):
        """Finalize deletion of any Entities that are marked as dead.

        In the interest of performance, this method duplicates code from the
        `delete_entity` method. If that method is changed, those changes should
        be duplicated here as well.
        """
        for entity in self._dead_entities:

            for component_type in self._entities[entity]:
                self._components[component_type].discard(entity)

                if not self._components[component_type]:
                    del self._components[component_type]

            del self._entities[entity]

        self._dead_entities.clear()
        self.clear_cache()

    def _process(self, *args, **kwargs):
        for processor in self._processors:
            processor.process(*args, **kwargs)

    def _timed_process(self, *args, **kwargs):
        """Track Processor execution time for benchmarking."""
        for processor in self._processors:
            start_time = _time.process_time()
            processor.process(*args, **kwargs)
            process_time = int(round((_time.process_time() - start_time) * 1000, 2))
            self.process_times[processor.__class__.__name__] = process_time

    def process(self, *args, **kwargs):
        """Call the process method on all Processors, in order of their priority.

        Call the :py:meth:`esper.Processor.process` method on all assigned Processors,
        respecting their optional priority setting. In addition, any Entities
        that were marked for deletion since the last call will be deleted
        at the start of this call.
        """
        self._clear_dead_entities()
        self._process(*args, **kwargs)
