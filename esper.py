import time as _time

from functools import lru_cache as _lru_cache
from typing import Dict, List, Type, TypeVar, Any, Tuple, Iterable, Set

C = TypeVar('C')
P = TypeVar('P')


class Processor:
    """Base class for all Processors to inherit from.

    Processor instances must contain a `process` method. Other than that,
    you are free to add any additional methods that are necessary. The process
    method will be called by each call to `World.process`, so you will
    generally want to iterate over entities with one (or more) calls to the
    appropriate world methods there, such as
    `for ent, (rend, vel) in self.world.get_components(Renderable, Velocity):`
    """
    world = None

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
        self._parent_relations = {}
        self._child_relations = {}
        if timed:
            self.process_times = {}
            self._process = self._timed_process

    def clear_cache(self) -> None:
        self.get_component.cache_clear()
        self.get_components.cache_clear()

    def clear_database(self) -> None:
        """Remove all Entities and Components from the World."""
        self._next_entity_id = 0
        self._dead_entities.clear()
        self._components.clear()
        self._entities.clear()
        self.clear_cache()

    def add_processor(self, processor_instance: Processor, priority=0) -> None:
        """Add a Processor instance to the World.

        :param processor_instance: An instance of a Processor,
               subclassed from the Processor class
        :param priority: A higher number is processed first.
        """
        assert issubclass(processor_instance.__class__, Processor)
        processor_instance.priority = priority
        processor_instance.world = self
        self._processors.append(processor_instance)
        self._processors.sort(key=lambda proc: proc.priority, reverse=True)

    def remove_processor(self, processor_type: Processor) -> None:
        """Remove a Processor from the World, by type.

        :param processor_type: The class type of the Processor to remove.
        """
        for processor in self._processors:
            if type(processor) == processor_type:
                processor.world = None
                self._processors.remove(processor)

    def get_processor(self, processor_type: Type[P]) -> P:
        """Get a Processor instance, by type.

        This method returns a Processor instance by type. This could be
        useful in certain situations, such as wanting to call a method on a
        Processor, from within another Processor.

        :param processor_type: The type of the Processor you wish to retrieve.
        :return: A Processor instance that has previously been added to the World.
        """
        for processor in self._processors:
            if type(processor) == processor_type:
                return processor

    def create_entity(self, *components) -> int:
        """Create a new Entity.

        This method returns an Entity ID, which is just a plain integer.
        You can optionally pass one or more Component instances to be
        assigned to the Entity.

        :param components: Optional components to be assigned to the
               entity on creation.
        :return: The next Entity ID in sequence.
        """
        self._next_entity_id += 1

        # TODO: duplicate add_component code here for performance
        for component in components:
            self.add_component(self._next_entity_id, component)

        # self.clear_cache()
        return self._next_entity_id

    def delete_entity(self, entity: int, immediate=False) -> None:
        """Delete an Entity from the World.

        Delete an Entity and all of it's assigned Component instances from
        the world. By default, Entity deletion is delayed until the next call
        to *World.process*. You can request immediate deletion, however, by
        passing the "immediate=True" parameter. This should generally not be
        done during Entity iteration (calls to World.get_component/s).

        Raises a KeyError if the given entity does not exist in the database.
        :param entity: The Entity ID you wish to delete.
        :param immediate: If True, delete the Entity immediately.
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

    def component_for_entity(self, entity: int, component_type: Type[C]) -> C:
        """Retrieve a Component instance for a specific Entity.

        Retrieve a Component instance for a specific Entity. In some cases,
        it may be necessary to access a specific Component instance.
        For example: directly modifying a Component to handle user input.

        Raises a KeyError if the given Entity and Component do not exist.
        :param entity: The Entity ID to retrieve the Component for.
        :param component_type: The Component instance you wish to retrieve.
        :return: The Component instance requested for the given Entity ID.
        """
        return self._entities[entity][component_type]

    def components_for_entity(self, entity: int) -> Tuple[C, ...]:
        """Retrieve all Components for a specific Entity, as a Tuple.

        Retrieve all Components for a specific Entity. The method is probably
        not appropriate to use in your Processors, but might be useful for
        saving state, or passing specific Components between World instances.
        Unlike most other methods, this returns all of the Components as a
        Tuple in one batch, instead of returning a Generator for iteration.

        Raises a KeyError if the given entity does not exist in the database.
        :param entity: The Entity ID to retrieve the Components for.
        :return: A tuple of all Component instances that have been
        assigned to the passed Entity ID.
        """
        return tuple(self._entities[entity].values())

    def has_component(self, entity: int, component_type: Any) -> bool:
        """Check if a specific Entity has a Component of a certain type.

        :param entity: The Entity you are querying.
        :param component_type: The type of Component to check for.
        :return: True if the Entity has a Component of this type,
                 otherwise False
        """
        return component_type in self._entities[entity]

    def add_component(self, entity: int, component_instance: Any) -> None:
        """Add a new Component instance to an Entity.

        Add a Component instance to an Entiy. If a Component of the same type
        is already assigned to the Entity, it will be replaced.

        :param entity: The Entity to associate the Component with.
        :param component_instance: A Component instance.
        """
        component_type = type(component_instance)

        if component_type not in self._components:
            self._components[component_type] = set()

        self._components[component_type].add(entity)

        if entity not in self._entities:
            self._entities[entity] = {}

        self._entities[entity][component_type] = component_instance
        self.clear_cache()

    def remove_component(self, entity: int, component_type: Any) -> int:
        """Remove a Component instance from an Entity, by type.

        A Component instance can be removed by providing it's type.
        For example: world.delete_component(enemy_a, Velocity) will remove
        the Velocity instance from the Entity enemy_a.

        Raises a KeyError if either the given entity or Component type does
        not exist in the database.
        :param entity: The Entity to remove the Component from.
        :param component_type: The type of the Component to remove.
        """
        self._components[component_type].discard(entity)

        if not self._components[component_type]:
            del self._components[component_type]

        del self._entities[entity][component_type]

        if not self._entities[entity]:
            del self._entities[entity]

        self.clear_cache()
        return entity

    def add_relationship(self, parent: int, child: int, component_type: Type[C]) -> None:
        """Add a new relation between two Components.

        Add a new relation between two Components, that must already exist in
        the World. This could be used for things like:

        renderable_a = World.create_component(Renderable())
        renderable_a = World.create_component(Renderable())
        World.add_relation(renderable_a, renderable_a, Renderable)

        The two renderables are related through the Renderable component type
        and can be retrieved in their parent/child order.

        :param parent: Entity acting as the parent.
        :param child: Entity acting as the child.
        :param component_type: The type of component that forms a relation.
        """
        self._parent_relations.setdefault(component_type, {})
        self._child_relations.setdefault(component_type, {})

        self._parent_relations[component_type].setdefault(parent, set())
        self._parent_relations[component_type][parent].add(child)

        current_parent = self._child_relations[component_type].get(child)
        self._child_relations[component_type][child] = parent

        if current_parent:
            self._parent_relations[component_type][current_parent].remove(child)
            if not self._parent_relations[component_type][current_parent]:
                del self._parent_relations[component_type][current_parent]
        self.clear_cache()

    def remove_relationship(self, parent: int, child: int, component_type: Type[C]) -> None:
        """Remove a relation between two Components.

        Raises a KeyError if the given relationship does not exist.
        :param parent: Entity acting as the parent.
        :param child: Entity acting as the child.
        :param component_type: The type of Component between parent and child.
        """
        if (parent in self._parent_relations[component_type] and
                child in self._parent_relations[component_type][parent]):
            self._parent_relations[component_type][parent].remove(child)
            if not self._parent_relations[component_type][parent]:
                del self._parent_relations[component_type][parent]
        if child in self._child_relations[component_type]:
            del self._child_relations[component_type][child]
        self.clear_cache()

    def has_relationship(self, parent: int, child: int, component_type: Type[C]) -> bool:
        """Check if a parent has a child.

        :param parent: Entity acting as the parent.
        :param child: Entity acting as the child.
        :param component_type: The type of Component between parent and child.
        :return: True if parent has child, otherwise False.
        """
        return self._child_relations.get(component_type, {}).get(child) == parent

    def get_parent(self, entity: int, component_type: Type[C]) -> int:
        """Retrieve the given entity's parent, if one exists

        :param entity: The child entity.
        :param component_type: The type of Component between parent and child.
        :return: Parent entity if one is found, None if given entity has no parent.
        """
        return self._child_relations.get(component_type, {}).get(entity)

    def get_children(self, entity: int, component_type: Type[C]) -> Set[int]:
        """Retrieve the given entity's children

        :param entity: The parent entity.
        :param component_type: The type of Component between parent and child.
        :return: Set of child entities. An empty set is returned if none are found.
        """
        return self._parent_relations.get(component_type, {}).get(entity, set())

    def _get_relationship_order(self, component_type: Type[C]) -> Dict[C, int]:
        """Get the order in which components are related to each other.

        :param component_type: The type of component to get the order for.
        :return: A dictionary mapping an entity to it's order.
        """
        compiled = []
        all_parents = self._parent_relations.get(component_type, {})
        all_children = self._child_relations.get(component_type, {})
        root_parents = [p for p in all_parents.keys() if p not in all_children]

        def get_children(parent, parents):
            rtn = [parent]
            for child in parents[parent]:
                if child in parents:
                    rtn += get_children(child, parents)
                else:
                    rtn.append(child)
            return rtn

        for root_parent in root_parents:
            compiled += get_children(root_parent, all_parents)

        return {x: i for i, x in enumerate(compiled)}

    def _get_component(self, component_type: Type[C], ordered: bool = False) -> Iterable[Tuple[int, C]]:
        """Get an iterator for Entity, Component pairs.

        :param component_type: The Component type to retrieve.
        :return: An iterator for (Entity, Component) tuples.
        """
        entity_db = self._entities

        components = list(self._components.get(component_type, []))
        if ordered:
            sort_order = self._get_relationship_order(component_type)
            components.sort(key=lambda i: sort_order.get(i, -1))
        for entity in components:
            yield entity, entity_db[entity][component_type]

    def _get_components(self, *component_types: Type, order_by: Type[C] = None) -> Iterable[Tuple[int, ...]]:
        """Get an iterator for Entity and multiple Component sets.

        :param component_types: Two or more Component types.
        :return: An iterator for Entity, (Component1, Component2, etc)
        tuples.
        """
        entity_db = self._entities
        comp_db = self._components

        try:
            intersections = set.intersection(
                *[comp_db[ct] for ct in component_types])
            if order_by:
                sort_order = self._get_relationship_order(order_by)
                list(intersections).sort(key=lambda i: sort_order.get(i, -1))
            for entity in intersections:
                yield entity, [entity_db[entity][ct] for ct in component_types]
        except KeyError:
            pass

    @_lru_cache()
    def get_component(self, component_type: Type[C], ordered: bool = False) -> List[Tuple[int, C]]:
        return [query for query in self._get_component(component_type, ordered=ordered)]

    @_lru_cache()
    def get_components(self, *component_types: Type, order_by: Type = None):
        return [query for query in self._get_components(*component_types, order_by=order_by)]

    def try_component(self, entity: int, component_type: Type):
        """Try to get a single component type for an Entity.

        This method will return the requested Component if it exists, but
        will pass silently if it does not. This allows a way to access optional
        Components that may or may not exist.

        :param entity: The Entity ID to retrieve the Component for.
        :param component_type: The Component instance you wish to retrieve.
        :return: A iterator containg the single Component instance requested,
                 which is empty if the component doesn't exist.
        """
        if component_type in self._entities[entity]:
            yield self._entities[entity][component_type]
        else:
            return None

    def _clear_dead_entities(self):
        """Finalize deletion of any Entities that are marked dead.

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
            process_time = int(
                round((_time.process_time() - start_time) * 1000, 2))
            self.process_times[processor.__class__.__name__] = process_time

    def process(self, *args, **kwargs):
        """Call the process method on all Processors, in order of their priority.

        Call the *process* method on all assigned Processors, respecting their
        optional priority setting. In addition, any Entities that were marked
        for deletion since the last call to *World.process*, will be deleted
        at the start of this method call.

        :param args: Optional arguments that will be passed through to the
                     *process* method of all Processors.
        """
        self._clear_dead_entities()
        self._process(*args, **kwargs)


CachedWorld = World
