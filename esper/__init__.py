"""esper is a lightweight Entity System (ECS) for Python, with a focus on performance

More information is available at https://github.com/benmoran56/esper
"""
from __future__ import annotations

import time as _time

from types import MethodType as _MethodType

from typing import Any as _Any
from typing import Callable as _Callable
from typing import TypeVar as _TypeVar
from typing import Iterable as _Iterable
from typing import overload as _overload

from weakref import ref as _ref
from weakref import WeakMethod as _WeakMethod

from math import inf

from itertools import count as _count

__version__ = version = '3.6'


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
    func_ref = _ref(func)
    if func_ref not in event_registry.get(name, []):
        return

    event_registry[name].remove(func_ref)
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

    Processor instances must define a :py:meth:`process` method, but you are
    otherwise free to define the class any way you wish. Processors should be
    instantiated, and then added to the current World context by calling
    :py:func:`esper.add_processor`. For example::

        my_processor_instance = MyProcessor()
        esper.add_processor(my_processor_instance)

    All the Processors that have been added to the World context will have
    their :py:meth:`esper.Processor.process` methods called by a single call
    to :py:func:`esper.process`. Inside the :py:meth:`process` method is
    where you should iterate over Entities with one (or more) calls to the
    appropriate esper functions::

        def process(self):
            for ent, (rend, vel) in esper.get_components(Renderable, Velocity):
                your_code_here()
    """

    priority = 0

    def process(self, *args: _Any, **kwargs: _Any) -> None:
        raise NotImplementedError


###########################################
#   World Context template and functions
###########################################

# Global variables that contain the state of the current world context:
_current_world: str = "default"
_entity_count: _count[int] = _count(start=1)
_components: dict[type[_Any], set[_Any]] = {}
_entities: dict[int, dict[type[_Any], _Any]] = {}
_dead_entities: set[int] = set()
_get_component_cache: dict[type[_Any], list[_Any]] = {}
_get_components_cache: dict[tuple[type[_Any], ...], list[_Any]] = {}
_processors: list[Processor] = []
_processors_dict: dict[type[Processor], Processor] = {}
_cache_dirty: bool = False
event_registry: dict[str, _Any] = {}
process_times: dict[str, int] = {}
# 'public' alias that gets set when switching worlds:
current_world: str = _current_world

# The _context_map holds all variables for the active & inactive contexts.
# We initialize it with default values::
_context_map: dict[str, tuple[
    _count[int],
    dict[type[_Any], set[_Any]],
    dict[int, dict[type[_Any], _Any]],
    set[int],
    dict[type[_Any], list[_Any]],
    dict[tuple[type[_Any], ...], list[_Any]],
    list[Processor],
    dict[type[Processor], Processor],
    bool,
    dict[str, int],
    dict[str, _Any]
]] = {_current_world: (_entity_count, {}, {}, set(), {}, {}, [], {}, False, {}, {})}


def list_worlds() -> list[str]:
    """A list all World context names."""
    return list(_context_map)


def delete_world(name: str) -> None:
    """Delete a World context.

    This will completely delete the World, including all entities
    that are contained within it.

    Raises `PermissionError` if you attempt to delete the currently
    active World context.
    """
    if _current_world == name:
        raise PermissionError("The active World context cannot be deleted.")

    del _context_map[name]


def switch_world(name: str) -> None:
    """Switch to a new World context by name.

    Esper can have one or more "Worlds". Each World is a dedicated
    context, and does not share Entities, Components, events, etc.
    Some game designs can benefit from using a dedicated World
    for each scene. For other designs, a single World may be sufficient.

    This function will allow you to create and switch between as
    many World contexts as required. If the requested name does not
    exist, a new context is created automatically with that name.

    The name of the currently active World context can be checked
    by examining :py:attr:`esper.current_world` attribute. This
    attribute gets updated whenever you switch Worlds.

    .. note:: At startup, a "default" World context is active.
    """
    if name not in _context_map:
        _context_map[name] = (_count(start=1), {}, {}, set(), {}, {}, [], {}, False, {}, {})

    global _current_world
    global _entity_count
    global _components
    global _entities
    global _dead_entities
    global _get_component_cache
    global _get_components_cache
    global _processors
    global _processors_dict
    global _cache_dirty
    global process_times
    global event_registry
    global current_world

    (_entity_count, _components, _entities, _dead_entities, _get_component_cache,
     _get_components_cache, _processors, _processors_dict, _cache_dirty,
     process_times, event_registry) = _context_map[name]
    _current_world = current_world = name


#####################
#   ECS functions
#####################

def clear_cache() -> None:
    """Manually clear the Component lookup cache.

    Clearing the cache is not necessary to do manually,
    but may be useful for benchmarking or debugging.
    """
    global _cache_dirty
    _cache_dirty = True


def _clear_cache_now() -> None:
    """Actually clear the cache (internal use)."""
    global _cache_dirty
    _get_component_cache.clear()
    _get_components_cache.clear()
    _cache_dirty = False


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
    _clear_cache_now()


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
    _processors_dict[type(processor_instance)] = processor_instance


def remove_processor(processor_type: type[Processor]) -> None:
    """Remove a Processor from the World, by type.

    Make sure to provide the class itself, **not** an instance. For example::

        # OK:
        self.world.remove_processor(MyProcessor)

        # NG:
        self.world.remove_processor(my_processor_instance)

    """
    processor = _processors_dict.pop(processor_type, None)
    if processor:
        _processors.remove(processor)


def get_processor(processor_type: type[Processor]) -> Processor | None:
    """Get a Processor instance, by type.

    This function returns a Processor instance by type. This could be
    useful in certain situations, such as wanting to call a method on a
    Processor, from within another Processor.
    """
    return _processors_dict.get(processor_type)


def create_entity(*components: _C) -> int:
    """Create a new Entity, with optional initial Components.

    This function returns an Entity ID, which is a plain integer.
    You can optionally pass one or more Component instances to be
    assigned to the Entity on creation. Components can be also be
    added later with the :py:func:`esper.add_component` function.
    """
    entity = next(_entity_count)
    entity_dict = {}

    for component_instance in components:
        component_type = type(component_instance)

        if component_type not in _components:
            _components[component_type] = set()

        _components[component_type].add(entity)
        entity_dict[component_type] = component_instance

    _entities[entity] = entity_dict
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
        entity_comps = _entities[entity]
        for component_type in entity_comps:
            comp_set = _components[component_type]
            comp_set.discard(entity)

            if not comp_set:
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


def component_for_entity(entity: int, component_type: type[_C]) -> _C:
    """Retrieve a Component instance for a specific Entity.

    Retrieve a Component instance for a specific Entity. In some cases,
    it may be necessary to access a specific Component instance.
    For example: directly modifying a Component to handle user input.

    Raises a KeyError if the given Entity and Component do not exist.
    """
    return _entities[entity][component_type]  # type: ignore[no-any-return]


def components_for_entity(entity: int) -> tuple[_C, ...]:
    """Retrieve all Components for a specific Entity, as a Tuple.

    Retrieve all Components for a specific Entity. This function is probably
    not appropriate to use in your Processors, but might be useful for
    saving state, or passing specific Components between World contexts.
    Unlike most other functions, this returns all the Components as a
    Tuple in one batch, instead of returning a Generator for iteration.

    Raises a KeyError if the given entity does not exist in the database.
    """
    return tuple(_entities[entity].values())


def has_component(entity: int, component_type: type[_C]) -> bool:
    """Check if an Entity has a specific Component type."""
    return component_type in _entities[entity]


def has_components(entity: int, *component_types: type[_C]) -> bool:
    """Check if an Entity has all the specified Component types."""
    entity_comps = _entities[entity]
    return all(comp_type in entity_comps for comp_type in component_types)


def add_component(entity: int, component_instance: _C, type_alias: type[_C] | None = None) -> None:
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


def remove_component(entity: int, component_type: type[_C]) -> _C:
    """Remove a Component instance from an Entity, by type.

    A Component instance can only be removed by providing its type.
    For example: esper.delete_component(enemy_a, Velocity) will remove
    the Velocity instance from the Entity enemy_a.

    Raises a KeyError if either the given entity or Component type does
    not exist in the database.
    """
    comp_set = _components[component_type]
    comp_set.discard(entity)

    if not comp_set:
        del _components[component_type]

    clear_cache()
    return _entities[entity].pop(component_type)  # type: ignore[no-any-return]


def try_remove_component(entity: int, component_type: type[_C]) -> _C | None:
    """Try to remove a Component instance from an Entity, by type.

    This operation is similar to :py:func:`esper.remove_component`, but
    will NOT raise an exception if the Component does not exist.
    """
    if comp_set := _components.get(component_type):
        comp_set.discard(entity)

        if not comp_set:
            del _components[component_type]

        clear_cache()
        return _entities[entity].pop(component_type)  # type: ignore[no-any-return]

    return None


def _get_component(component_type: type[_C]) -> _Iterable[tuple[int, _C]]:
    entity_db = _entities
    comp_set = _components.get(component_type)

    if comp_set is None:
        return

    for entity in comp_set:
        yield entity, entity_db[entity][component_type]


def _get_components(*component_types: type[_C]) -> _Iterable[tuple[int, tuple[_C, ...]]]:
    if not component_types:
        return

    entity_db = _entities
    comp_db = _components

    min_set = None
    min_size = inf
    other_types = []

    for ct in component_types:
        comp_set = comp_db.get(ct)
        if comp_set is None:
            return
        set_size = len(comp_set)
        if set_size < min_size:
            if min_set is not None:
                other_types.append(component_types[len(other_types)])
            min_size = set_size
            min_set = comp_set
        else:
            other_types.append(ct)

    if min_set is None:
        return

    if not other_types:
        for entity in min_set:
            entity_comps = entity_db[entity]
            yield entity, tuple(entity_comps[ct] for ct in component_types)
    else:
        for entity in min_set:
            entity_comps = entity_db[entity]
            has_all = True
            for ct in other_types:
                if ct not in entity_comps:
                    has_all = False
                    break
            if has_all:
                yield entity, tuple(entity_comps[ct] for ct in component_types)


def get_component(component_type: type[_C]) -> list[tuple[int, _C]]:
    """Get an iterator for Entity, Component pairs."""
    if _cache_dirty:
        _clear_cache_now()

    cached = _get_component_cache.get(component_type)
    if cached is not None:
        return cached

    result = list(_get_component(component_type))
    _get_component_cache[component_type] = result
    return result


@_overload
def get_components(__c1: type[_C], __c2: type[_C2]) -> list[tuple[int, tuple[_C, _C2]]]:
    ...


@_overload
def get_components(__c1: type[_C], __c2: type[_C2], __c3: type[_C3]) -> list[tuple[int, tuple[_C, _C2, _C3]]]:
    ...


@_overload
def get_components(__c1: type[_C], __c2: type[_C2], __c3: type[_C3], __c4: type[_C4]) -> list[
                   tuple[int, tuple[_C, _C2, _C3, _C4]]]:
    ...


def get_components(*component_types: type[_Any]) -> list[tuple[int, tuple[_Any, ...]]]:
    """Get an iterator for Entity and multiple Component sets."""
    if _cache_dirty:
        _clear_cache_now()

    cached = _get_components_cache.get(component_types)
    if cached is not None:
        return cached

    result = list(_get_components(*component_types))
    _get_components_cache[component_types] = result
    return result


def try_component(entity: int, component_type: type[_C]) -> _C | None:
    """Try to get a single component type for an Entity.

    This function will return the requested Component if it exists,
    or None if it does not. This allows a way to access optional Components
    that may or may not exist, without having to first query if the Entity
    has the Component type.
    """
    entity_comps = _entities.get(entity)
    if entity_comps and component_type in entity_comps:
        return entity_comps[component_type]  # type: ignore[no-any-return]
    return None


@_overload
def try_components(entity: int, __c1: type[_C], __c2: type[_C2]) -> tuple[_C, _C2]:
    ...


@_overload
def try_components(entity: int, __c1: type[_C], __c2: type[_C2], __c3: type[_C3]) -> tuple[_C, _C2, _C3]:
    ...


@_overload
def try_components(entity: int, __c1: type[_C], __c2: type[_C2], __c3: type[_C3], __c4: type[_C4]) -> tuple[_C, _C2, _C3, _C4]:
    ...


def try_components(entity: int, *component_types: type[_C]) -> tuple[_C, ...] | None:
    """Try to get multiple component types for an Entity.

    This function will return the requested Components if they exist,
    or None if they do not. This allows a way to access optional Components
    that may or may not exist, without first having to query if the Entity
    has the Component types.
    """
    entity_comps = _entities.get(entity)
    if entity_comps and all(comp_type in entity_comps for comp_type in component_types):
        return tuple(entity_comps[comp_type] for comp_type in component_types)
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
    if not _dead_entities:
        return

    for entity in _dead_entities:
        entity_comps = _entities[entity]

        for component_type in entity_comps:
            comp_set = _components[component_type]
            comp_set.discard(entity)

            if not comp_set:
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
    (in milliseconds) in the :py:attr:`~process_times` dictionary
    after each call.
    """
    clear_dead_entities()
    for processor in _processors:
        start_time = _time.process_time()
        processor.process(*args, **kwargs)
        process_times[processor.__class__.__name__] = int((_time.process_time() - start_time) * 1000)
