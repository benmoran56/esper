# -*- coding: utf-8 -*-

import sys

try:
    from functools import lru_cache
except ImportError:
    from backports.functools_lru_cache import lru_cache


class World(object):
    def __init__(self):
        """A World object keeps track of all Entities, Components and Processors.

        A World contains a database of all Entity/Component assignments. It also
        handles calling the process method on any Processors assigned to it.
        """
        self._processors = []
        self._next_entity_id = 0
        self._components = {}
        self._entities = {}

    def clear_database(self):
        """Remove all entities and components from the world."""
        self._components.clear()
        self._entities.clear()
        self._next_entity_id = 0

    def add_processor(self, processor_instance, priority=0):
        """Add a Processor instance to the world.

        :param processor_instance: An instance of a Processor,
        subclassed from the Processor class
        :param priority: A higher number is processed first.
        """
        # TODO: raise an exception if the same type Processor already exists.
        # TODO: check that the processor is a subclass of esper.Processor.
        processor_instance.priority = priority
        processor_instance.world = self
        self._processors.append(processor_instance)
        self._processors.sort(key=lambda processor: -processor.priority)

    def remove_processor(self, processor_type):
        """Remove a Processor from the world, by type.

        :param processor_type: The class type of the Processor to remove.
        """
        for processor in self._processors:
            if type(processor) == processor_type:
                processor.world = None
                self._processors.remove(processor)

    def create_entity(self):
        """Create a new Entity.

        This method return an Entity ID, which is just a plain integer.
        :return: The next Entity ID in sequence.
        """
        self._next_entity_id += 1
        return self._next_entity_id

    def delete_entity(self, entity):
        """Delete an Entity from the World.

        Delete an Entity from the World. This will also delete any Component
        instances that are assigned to the Entity.
        :param entity: The Entity ID you wish to delete.
        """
        for component_type in self._entities.get(entity, []):
            self._components[component_type].discard(entity)

            if not self._components[component_type]:
                del self._components[component_type]

        try:
            del self._entities[entity]
            return entity
        except KeyError:
            pass

    def component_for_entity(self, entity, component_type):
        """Retrieve a specific Component instance for an Entity.

        :param entity: The Entity to retrieve the Component for.
        :param component_type: The Component instance you wish to retrieve.
        :return: A Component instance, *if* it exists for the Entity.
        """
        try:
            return self._entities[entity][component_type]
        except KeyError:
            pass

    def add_component(self, entity, component_instance):
        """Add a new Component instance to an Entity.

        If a Component of the same type is already assigned to the Entity,
        it will be replaced with the new one.
        :param entity: The Entity to associate the Component with.
        :param component_instance: A Component instance.
        """
        if not isinstance(component_instance, object):
            raise TypeError("Component must be a new-style class instance "
                            "(derive from object).")

        component_type = type(component_instance)

        if component_type not in self._components:
            self._components[component_type] = set()

        self._components[component_type].add(entity)

        if entity not in self._entities:
            self._entities[entity] = {}

        self._entities[entity][component_type] = component_instance

    def delete_component(self, entity, component_type):
        """Delete a Component instance from an Entity, by type.

        An Component instance can be Deleted by providing it's type.
        For example: world.delete_component(enemy_a, Velocity) will remove
        the Velocity instance from the Entity enemy_a.

        :param entity: The Entity to delete the Component from.
        :param component_type: The type of the Component to remove.
        """
        try:
            self._components[component_type].discard(entity)

            if not self._components[component_type]:
                del self._components[component_type]
        except KeyError:
            pass

        try:
            del self._entities[entity][component_type]

            if not self._entities[entity]:
                del self._entities[entity]

            return entity
        except KeyError:
            pass

    def get_component(self, component_type):
        """Get an iterator for Entity, Component pairs.

        :param component_type: The Component type to retrieve.
        :return: An iterator for (Entity, Component) tuples.
        """
        entity_db = self._entities
        for entity in self._components.get(component_type, []):
            yield entity, entity_db[entity][component_type]

    def get_components(self, *component_types):
        """Get an iterator for Entity and multiple Component sets.

        :param component_types: Two or more Component types.
        :return: An iterator for (Entity, Component1, Component2, etc)
        tuples.
        """
        entity_db = self._entities
        comp_db = self._components

        try:
            entity_set = set.intersection(*[comp_db[ct] for ct in component_types])
            for entity in entity_set:
                yield entity, [entity_db[entity][ct] for ct in component_types]
        except KeyError:
            pass

    def process(self, *args):
        """Process all Systems, in order of their priority."""
        for processor in self._processors:
            processor.process(*args)


class CachedWorld(World):
    def __init__(self, cache_size=128):
        """A sub-class of World using an LRU cache for Entity lookups."""
        super(CacheWorld, self).__init__()
        self.set_cache_size(cache_size)

    def set_cache_size(self, size):
        """Set the maximum size of the LRU cache for Entity lookup.

        Replaces the existing cache.
        """
        wrapped = self._get_entities.__wrapped__.__get__(self, World)
        self._get_entities = lru_cache(size)(wrapped)

    def clear_database(self):
        """Remove all Entities and Components from the world."""
        super(CachedWorld, self).clear_database()
        self._get_entities.cache_clear()

    def delete_entity(self, entity):
        """Delete an Entity from the World."""
        if super(CachedWorld, self).delete_entity(entity) is not None:
            self._get_entities.cache_clear()
            return entity

    def add_component(self, entity, component_instance):
        """Add a new Component instance to an Entity."""
        super(CachedWorld, self).add_component(entity, component_instance)
        self._get_entities.cache_clear()

    def delete_component(self, entity, component_type):
        """Delete a Component instance from an Entity, by type."""
        if super(CachedWorld, self).delete_component(
                entity, component_instance) is not None:
            self._get_entities.cache_clear()
            return entity

    @lru_cache()
    def _get_entities(self, component_types):
        """Return set of Entities having all given Components."""
        comp_db = self._components
        return set.intersection(*[comp_db[ct] for ct in component_types])

    def get_components(self, *component_types):
        """Get an iterator for Entity and multiple Component sets."""
        entity_db = self._entities
        try:
            for entity in self._get_entities(component_types):
                yield entity, [entity_db[entity][ct] for ct in component_types]
        except KeyError:
            pass
