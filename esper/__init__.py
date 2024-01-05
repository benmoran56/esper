"""esper is a lightweight Entity System (ECS) for Python, with a focus on performance

More information is available at https://github.com/benmoran56/esper
"""
import time as _time

from types import MethodType as _MethodType

from typing import Any as _Any
from typing import Callable as _Callable
from typing import Dict as _Dict
from typing import List as _List
from typing import Set as _Set
from typing import Type as _Type
from typing import Tuple as _Tuple
from typing import TypeVar as _TypeVar
from typing import Iterable as _Iterable
from typing import Optional as _Optional
from typing import overload as _overload

from weakref import ref as _ref
from weakref import WeakMethod as _WeakMethod

from itertools import count as _count

__version__ = version = '3.2'


###################
#  Event system
###################


def dispatch_event(name: str, *args: _Any) -> None:
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


def _make_callback(name: str) -> _Callable[[_Any], None]:
    """Create an internal callback to remove dead handlers."""

    def callback(weak_method: _Any) -> None:
        event_registry[name].remove(weak_method)
        if not event_registry[name]:
            del event_registry[name]

    return callback


def set_handler(name: str, func: _Callable[..., None]) -> None:
    """Register a function to handle the named event type.

    After registering a function (or method), it will receive all
    events that are dispatched by the specified name.

    .. note:: A weak reference is kept to the passed function,
    """
    if name not in event_registry:
        event_registry[name] = set()

    if isinstance(func, _MethodType):
        event_registry[name].add(_WeakMethod(func, _make_callback(name)))
    else:
        event_registry[name].add(_ref(func, _make_callback(name)))


def remove_handler(name: str, func: _Callable[..., None]) -> None:
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
_C2 = _TypeVar('_C2')
_C3 = _TypeVar('_C3')
_C4 = _TypeVar('_C4')


class Processor:
    """Base class for all Processors to inherit from.

    Processor instances must contain a `process` method, but you are otherwise
    free to define the class any way you wish. Processors should be instantiated,
    and then added to the current World context by calling :py:func:`esper.add_processor`.
    For example::

        my_processor_instance = MyProcessor()
        esper.add_processor(my_processor_instance)

     All the Processors that have been added to the World context will have their
    :py:meth:`esper.Processor.process` methods called by a single call to
    :py:func:`esper.process`. Inside the `process` method is generally where you
    should iterate over Entities with one (or more) calls to the appropriate methods::

        def process(self):
            for ent, (rend, vel) in esper.get_components(Renderable, Velocity):
                your_code_here()
    """

    priority = 0

    def process(self, *args: _Any, **kwargs: _Any) -> None:
        raise NotImplementedError


###################
#   ECS functions
###################

_current_context: str = "default"
_entity_count: "_count[int]" = _count(start=1)
_components: _Dict[_Type[_Any], _Set[_Any]] = {}
_entities: _Dict[int, _Dict[_Type[_Any], _Any]] = {}
_dead_entities: _Set[int] = set()
_get_component_cache: _Dict[_Type[_Any], _List[_Any]] = {}
_get_components_cache: _Dict[_Tuple[_Type[_Any], ...], _List[_Any]] = {}
_processors: _List[Processor] = []
process_times: _Dict[str, int] = {}
event_registry: _Dict[str, _Any] = {}

# {context_name: (entity_count, components, entities, dead_entities, comp_cache, comps_cache, processors, process_times, event_registry)}
_context_map: _Dict[str, _Tuple[
    "_count[int]",
    _Dict[_Type[_Any], _Set[_Any]],
    _Dict[int, _Dict[_Type[_Any], _Any]],
    _Set[int],
    _Dict[_Type[_Any], _List[_Any]],
    _Dict[_Tuple[_Type[_Any], ...], _List[_Any]],
    _List[Processor],
    _Dict[str, int],
    _Dict[str, _Any]
]] = {"default": (_entity_count, {}, {}, set(), {}, {}, [], {}, {})}


def clear_cache() -> None:
    """Manually clear the Component lookup cache.

    Clearing the cache is not necessary to do manually,
    but may be useful for benchmarking or debugging.
    """
    _get_component_cache.clear()
    _get_components_cache.clear()


def clear_database() -> None:
    """Clear the Entity Component database.

    Removes all Entities and Components from the current World.
    Processors are not removed.
    """
    global _entity_count
    _entity_count = _count(start=1)
    _components.clear()
    _entities.clear()
    _dead_entities.clear()
    clear_cache()


def add_processor(processor_instance: Processor, priority: int = 0) -> None:
    """Add a Processor instance to the current World.

    Add a Processor instance to the world (subclass of
    :py:class:`esper.Processor`), with optional priority.

    When the :py:func:`esper.World.process` function is called,
    Processors with higher priority will be called first.
    """
    processor_instance.priority = priority
    _processors.append(processor_instance)
    _processors.sort(key=lambda proc: proc.priority, reverse=True)


def remove_processor(processor_type: _Type[Processor]) -> None:
    """Remove a Processor from the World, by type.

    Make sure to provide the class itself, **not** an instance. For example::

        # OK:
        self.world.remove_processor(MyProcessor)

        # NG:
        self.world.remove_processor(my_processor_instance)

    """
    for processor in _processors:
        if type(processor) is processor_type:
            _processors.remove(processor)


def get_processor(processor_type: _Type[Processor]) -> _Optional[Processor]:
    """Get a Processor instance, by type.

    This function returns a Processor instance by type. This could be
    useful in certain situations, such as wanting to call a method on a
    Processor, from within another Processor.
    """
    for processor in _processors:
        if type(processor) is processor_type:
            return processor
    else:
        return None


def create_entity(*components: _C) -> int:
    """Create a new Entity, with optional initial Components.

    This funcion returns an Entity ID, which is a plain integer.
    You can optionally pass one or more Component instances to be
    assigned to the Entity on creation. Components can be also be
    added later with the :py:func:`esper.add_component` funcion.
    """
    entity = next(_entity_count)

    if entity not in _entities:
        _entities[entity] = {}

    for component_instance in components:

        component_type = type(component_instance)

        if component_type not in _components:
            _components[component_type] = set()

        _components[component_type].add(entity)

        _entities[entity][component_type] = component_instance
        clear_cache()

    return entity


def delete_entity(entity: int, immediate: bool = False) -> None:
    """Delete an Entity from the current World.

    Delete an Entity and all of it's assigned Component instances from
    the world. By default, Entity deletion is delayed until the next call
    to :py:func:`esper.process`. You can, however, request immediate
    deletion by passing the `immediate=True` parameter. Note that immediate
    deletion may cause issues, such as when done during Entity iteration
    (calls to esper.get_component/s).

    Raises a KeyError if the given entity does not exist in the database.
    """
    if immediate:
        for component_type in _entities[entity]:
            _components[component_type].discard(entity)

            if not _components[component_type]:
                del _components[component_type]

        del _entities[entity]
        clear_cache()

    else:
        _dead_entities.add(entity)


def entity_exists(entity: int) -> bool:
    """Check if a specific Entity exists.

    Empty Entities (with no components) and dead Entities (destroyed
    by delete_entity) will not count as existent ones.
    """
    return entity in _entities and entity not in _dead_entities


def component_for_entity(entity: int, component_type: _Type[_C]) -> _C:
    """Retrieve a Component instance for a specific Entity.

    Retrieve a Component instance for a specific Entity. In some cases,
    it may be necessary to access a specific Component instance.
    For example: directly modifying a Component to handle user input.

    Raises a KeyError if the given Entity and Component do not exist.
    """
    return _entities[entity][component_type]  # type: ignore[no-any-return]


def components_for_entity(entity: int) -> _Tuple[_C, ...]:
    """Retrieve all Components for a specific Entity, as a Tuple.

    Retrieve all Components for a specific Entity. This function is probably
    not appropriate to use in your Processors, but might be useful for
    saving state, or passing specific Components between World contexts.
    Unlike most other functions, this returns all the Components as a
    Tuple in one batch, instead of returning a Generator for iteration.

    Raises a KeyError if the given entity does not exist in the database.
    """
    return tuple(_entities[entity].values())


def has_component(entity: int, component_type: _Type[_C]) -> bool:
    """Check if an Entity has a specific Component type."""
    return component_type in _entities[entity]


def has_components(entity: int, *component_types: _Type[_C]) -> bool:
    """Check if an Entity has all the specified Component types."""
    return all(comp_type in _entities[entity] for comp_type in component_types)


def add_component(entity: int, component_instance: _C, type_alias: _Optional[_Type[_C]] = None) -> None:
    """Add a new Component instance to an Entity.

    Add a Component instance to an Entiy. If a Component of the same type
    is already assigned to the Entity, it will be replaced.

    A `type_alias` can also be provided. This can be useful if you're using
    subclasses to organize your Components, but would like to query them
    later by some common parent type.
    """
    component_type = type_alias or type(component_instance)

    if component_type not in _components:
        _components[component_type] = set()

    _components[component_type].add(entity)

    _entities[entity][component_type] = component_instance
    clear_cache()


def remove_component(entity: int, component_type: _Type[_C]) -> _C:
    """Remove a Component instance from an Entity, by type.

    A Component instance can only be removed by providing its type.
    For example: esper.delete_component(enemy_a, Velocity) will remove
    the Velocity instance from the Entity enemy_a.

    Raises a KeyError if either the given entity or Component type does
    not exist in the database.
    """
    _components[component_type].discard(entity)

    if not _components[component_type]:
        del _components[component_type]

    clear_cache()
    return _entities[entity].pop(component_type)  # type: ignore[no-any-return]


def _get_component(component_type: _Type[_C]) -> _Iterable[_Tuple[int, _C]]:
    entity_db = _entities

    for entity in _components.get(component_type, []):
        yield entity, entity_db[entity][component_type]


def _get_components(*component_types: _Type[_C]) -> _Iterable[_Tuple[int, _List[_C]]]:
    entity_db = _entities
    comp_db = _components

    try:
        for entity in set.intersection(*[comp_db[ct] for ct in component_types]):
            yield entity, [entity_db[entity][ct] for ct in component_types]
    except KeyError:
        pass


def get_component(component_type: _Type[_C]) -> _List[_Tuple[int, _C]]:
    """Get an iterator for Entity, Component pairs."""
    try:
        return _get_component_cache[component_type]
    except KeyError:
        return _get_component_cache.setdefault(
            component_type, list(_get_component(component_type))
        )


@_overload
def get_components(__c1: _Type[_C], __c2: _Type[_C2]) -> _List[_Tuple[int, _Tuple[_C, _C2]]]:
    ...


@_overload
def get_components(__c1: _Type[_C], __c2: _Type[_C2], __c3: _Type[_C3]) -> _List[_Tuple[int, _Tuple[_C, _C2, _C3]]]:
    ...


@_overload
def get_components(__c1: _Type[_C], __c2: _Type[_C2], __c3: _Type[_C3], __c4: _Type[_C4]) -> _List[
    _Tuple[int, _Tuple[_C, _C2, _C3, _C4]]]:
    ...


def get_components(*component_types: _Type[_Any]) -> _Iterable[_Tuple[int, _Tuple[_Any, ...]]]:
    """Get an iterator for Entity and multiple Component sets."""
    try:
        return _get_components_cache[component_types]
    except KeyError:
        return _get_components_cache.setdefault(
            component_types, list(_get_components(*component_types))
        )


def try_component(entity: int, component_type: _Type[_C]) -> _Optional[_C]:
    """Try to get a single component type for an Entity.

    This function will return the requested Component if it exists,
    or None if it does not. This allows a way to access optional Components
    that may or may not exist, without having to first query if the Entity
    has the Component type.
    """
    if component_type in _entities[entity]:
        return _entities[entity][component_type]  # type: ignore[no-any-return]
    return None


@_overload
def try_components(entity: int, __c1: _Type[_C], __c2: _Type[_C2]) -> _Tuple[_C, _C2]:
    ...


@_overload
def try_components(entity: int, __c1: _Type[_C], __c2: _Type[_C2], __c3: _Type[_C3]) -> _Tuple[_C, _C2, _C3]:
    ...


@_overload
def try_components(entity: int, __c1: _Type[_C], __c2: _Type[_C2], __c3: _Type[_C3], __c4: _Type[_C4]) -> _Tuple[_C, _C2, _C3, _C4]:
    ...


def try_components(entity: int, *component_types: _Type[_C]) -> _Optional[_Tuple[_C, ...]]:
    """Try to get a multiple component types for an Entity.

    This function will return the requested Components if they exist,
    or None if they do not. This allows a way to access optional Components
    that may or may not exist, without first having to query if the Entity
    has the Component types.
    """
    if all(comp_type in _entities[entity] for comp_type in component_types):
        return [_entities[entity][comp_type] for comp_type in component_types]  # type: ignore[return-value]
    return None


def clear_dead_entities() -> None:
    """Finalize deletion of any Entities that are marked as dead.

    This function is provided for those who are not making use of
    :py:func:`esper.add_processor` and :py:func:`esper.process`. If you are
    calling your processors manually, this function should be called in
    your main loop after calling all processors.
    """
    # In the interest of performance, this function duplicates code from the
    # `delete_entity` function. If that function is changed, those changes should
    # be duplicated here as well.
    for entity in _dead_entities:

        for component_type in _entities[entity]:
            _components[component_type].discard(entity)

            if not _components[component_type]:
                del _components[component_type]

        del _entities[entity]

    _dead_entities.clear()
    clear_cache()


def process(*args: _Any, **kwargs: _Any) -> None:
    """Call the process method on all Processors, in order of their priority.

    Call the :py:meth:`esper.Processor.process` method on all assigned
    Processors, respective of their priority. In addition, any Entities
    that were marked for deletion since the last call will be deleted
    at the start of this call.
    """
    clear_dead_entities()
    for processor in _processors:
        processor.process(*args, **kwargs)


def timed_process(*args: _Any, **kwargs: _Any) -> None:
    """Track Processor execution time for benchmarking.

    This function is identical to :py:func:`esper.process`, but
    it additionally records the elapsed time of each processor
    call (in milliseconds) in the`esper.process_times` dictionary.
    """
    clear_dead_entities()
    for processor in _processors:
        start_time = _time.process_time()
        processor.process(*args, **kwargs)
        process_times[processor.__class__.__name__] = int((_time.process_time() - start_time) * 1000)


def list_worlds() -> _List[str]:
    """A list all World context names."""
    return list(_context_map)


def delete_world(name: str) -> None:
    """Delete a World context.

    This will completely delete the World, including all entities
    that are contained within it.

    Raises `PermissionError` if you attempt to delete the currently
    active World context.
    """
    if _current_context == name:
        raise PermissionError("The active World context cannot be deleted.")

    del _context_map[name]


def switch_world(name: str) -> None:
    """Switch to a new World context by name.

    Esper can have one or more "Worlds". Each World is a dedicated
    context, and does not share Entities, Components, events, etc.
    Some game designs can benefit from using a dedicated World
    for each scene. For other designs, a single World may
    be sufficient.

    This function will allow you to create and switch between as
    many World contexts as required. If the requested name does not
    exist, a new context is created automatically with that name.

    .. note:: At startup, a "default" World context is active.
    """
    if name not in _context_map:
        # Create a new context if the name does not already exist:
        _context_map[name] = (_count(start=1), {}, {}, set(), {}, {}, [], {}, {})

    global _current_context
    global _entity_count
    global _components
    global _entities
    global _dead_entities
    global _get_component_cache
    global _get_components_cache
    global _processors
    global process_times
    global event_registry

    # switch the references to the objects in the named context_map:
    (_entity_count, _components, _entities, _dead_entities, _get_component_cache,
     _get_components_cache, _processors, process_times, event_registry) = _context_map[name]
    _current_context = name


@property   # type: ignore
def current_world() -> str:
    """The currently active World context.

    To switch World contexts, see :py:func:`esper.switch_world`.
    """
    return _current_context
