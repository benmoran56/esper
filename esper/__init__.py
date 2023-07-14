from typing import Any as _Any
from typing import Dict as _Dict
from typing import List as _List
from typing import Set as _Set
from typing import Type as _Type
from typing import Tuple as _Tuple
from typing import TypeVar as _TypeVar
from typing import Iterable as _Iterable
from typing import Optional as _Optional
from typing import overload as _overload
from itertools import count as _count


version = '3.0'


_C = _TypeVar('_C')
_C2 = _TypeVar('_C2')
_C3 = _TypeVar('_C3')
_C4 = _TypeVar('_C4')


_entity_count: "_count[int]" = _count(start=1)
_components: _Dict[_Type[_Any], _Set[_Any]] = {}
_entities: _Dict[int, _Dict[_Type[_Any], _Any]] = {}
_dead_entities: _Set[int] = set()
_get_component_cache: _Dict[_Type[_Any], _List[_Any]] = {}
_get_components_cache: _Dict[_Tuple[_Type[_Any], ...], _List[_Any]] = {}

# {context_id: (entity_count, components, entities, dead_entities, comp_cache, comps_cache)}
_context_map: _Dict[str, _Tuple[
    "_count[int]",
    _Dict[_Type[_Any], _Set[_Any]],
    _Dict[int, _Dict[_Type[_Any], _Any]],
    _Set[int],
    _Dict[_Type[_Any], _List[_Any]],
    _Dict[_Tuple[_Type[_Any], ...], _List[_Any]],
]] = {}

def clear_cache() -> None:
    """Manually clear the internal cache."""
    _get_component_cache.clear()
    _get_components_cache.clear()


def clear_database() -> None:
    """Remove all Entities and Components from the World."""
    global _entity_count
    _dead_entities.clear()
    _entities.clear()
    _components.clear()
    _entity_count = _count(start=1)
    clear_cache()
    _context_map.clear()


def create_entity(*components: _C) -> int:
    """Create a new Entity, with optional Components.

    This method returns an Entity ID, which is a plain integer.
    You can optionally pass one or more Component instances to be
    assigned to the Entity on creation. Components can be also be
    added later with the :py:meth:`esper.add_component` method.
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
    """Delete an Entity from the World.

    Delete an Entity and all of it's assigned Component instances from
    the world. By default, Entity deletion is delayed until the next call
    to :py:meth:`esper.process`. You can, however, request immediate
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

    Retrieve all Components for a specific Entity. The method is probably
    not appropriate to use in your Processors, but might be useful for
    saving state, or passing specific Components between World instances.
    Unlike most other methods, this returns all the Components as a
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
def get_components(__c1: _Type[_C], __c2: _Type[_C2], __c3: _Type[_C3], __c4: _Type[_C4]) -> _List[_Tuple[int, _Tuple[_C, _C2, _C3, _C4]]]:
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

    This method will return the requested Component if it exists,
    or None if it does not. This allows a way to access optional Components
    that may or may not exist, without having to first query if the Entity
    has the Component type.
    """
    if component_type in _entities[entity]:
        return _entities[entity][component_type]  # type: ignore[no-any-return]
    return None


def try_components(entity: int, *component_types: _Type[_C]) -> _Optional[_List[_List[_C]]]:
    """Try to get a multiple component types for an Entity.

    This method will return the requested Components if they exist,
    or None if they do not. This allows a way to access optional Components
    that may or may not exist, without first having to query if the Entity
    has the Component types.
    """
    if all(comp_type in _entities[entity] for comp_type in component_types):
        return [_entities[entity][comp_type] for comp_type in component_types]
    return None


def clear_dead_entities() -> None:
    """Finalize deletion of any Entities that are marked as dead.

    In the interest of performance, this method duplicates code from the
    `delete_entity` method. If that method is changed, those changes should
    be duplicated here as well.
    This function should be called in main loop after systems.
    """
    for entity in _dead_entities:

        for component_type in _entities[entity]:
            _components[component_type].discard(entity)

            if not _components[component_type]:
                del _components[component_type]

        del _entities[entity]

    _dead_entities.clear()
    clear_cache()


def init_world(name: str) -> None:
    _context_map[name] = (_count(start=1), {}, {}, set(), {}, {})


def switch_world(name: str) -> None:
    global _entity_count
    global _components
    global _entities
    global _dead_entities
    global _get_component_cache
    global _get_components_cache
    _entity_count, _components, _entities, _dead_entities, _get_component_cache, _get_components_cache = _context_map[name]
