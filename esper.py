import time as _time

from functools import lru_cache as _lru_cache
from typing import List, Type, TypeVar, Dict, Any, Tuple, Iterable

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
    world = None # type: World

    def process(self, *args, **kwargs):
        raise NotImplementedError


class World:
    def __init__(self, timed=False):
        """A World object keeps track of all Entities, Components, and Processors.

        A World contains a database of all Entity/Component assignments. It also
        handles calling the process method on any Processors assigned to it.
        """
        self._processors = [] # type: List[Processor]
        self._next_entity_id = 0
        self._components = {}
        self._entities = {} # type: Dict[int, Any]
        self._dead_entities = set()
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

    def _get_component(self, component_type: Type[C]) -> Iterable[Tuple[int, C]]:
        """Get an iterator for Entity, Component pairs.

        :param component_type: The Component type to retrieve.
        :return: An iterator for (Entity, Component) tuples.
        """
        entity_db = self._entities

        for entity in self._components.get(component_type, []):
            yield entity, entity_db[entity][component_type]

    def _get_components(self, *component_types: Type)-> Iterable[Tuple[int, ...]]:
        """Get an iterator for Entity and multiple Component sets.

        :param component_types: Two or more Component types.
        :return: An iterator for Entity, (Component1, Component2, etc)
        tuples.
        """
        entity_db = self._entities
        comp_db = self._components

        try:
            for entity in set.intersection(*[comp_db[ct] for ct in component_types]):
                yield entity, [entity_db[entity][ct] for ct in component_types]
        except KeyError:
            pass

    @_lru_cache()
    def get_component(self, component_type: Type[C]) -> List[Tuple[int, C]]:
        return [query for query in self._get_component(component_type)]

    @_lru_cache()
    def get_components(self, *component_types: Type):
        return [query for query in self._get_components(*component_types)]

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
            process_time = int(round((_time.process_time() - start_time) * 1000, 2))
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
