import esper

from functools import lru_cache


class World:
    def __init__(self):
        """A World object keeps track of all Entities, Components, and Processors.

        A World contains a database of all Entity/Component assignments. It also
        handles calling the process method on any Processors assigned to it.
        """
        self._processors = []
        self._next_entity_id = 0
        self._components = {}
        self._entities = {}
        self._dead_entities = set()

    def clear_database(self):
        """Remove all Entities and Components from the World."""
        self._next_entity_id = 0
        self._components.clear()
        self._entities.clear()

    def add_processor(self, processor_instance, priority=0):
        """Add a Processor instance to the World.

        :param processor_instance: An instance of a Processor,
        subclassed from the esper.Processor class
        :param priority: A higher number is processed first.
        """
        assert issubclass(processor_instance.__class__, esper.Processor)
        processor_instance.priority = priority
        processor_instance.world = self
        self._processors.append(processor_instance)
        self._processors.sort(key=lambda proc: proc.priority, reverse=True)

    def remove_processor(self, processor_type):
        """Remove a Processor from the World, by type.

        :param processor_type: The class type of the Processor to remove.
        """
        for processor in self._processors:
            if type(processor) == processor_type:
                processor.world = None
                self._processors.remove(processor)

    def get_processor(self, processor_type):
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

    def create_entity(self, *components):
        """Create a new Entity.

        This method returns an Entity ID, which is just a plain integer.
        You can optionally pass one or more Component instances to be
        assigned to the Entity.

        :param components: Optional components to be assigned to the
        entity on creation.
        :return: The next Entity ID in sequence.
        """
        self._next_entity_id += 1

        for component in components:
            self.add_component(self._next_entity_id, component)

        return self._next_entity_id

    def delete_entity(self, entity, immediate=False):
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

        else:
            self._dead_entities.add(entity)

    def component_for_entity(self, entity, component_type):
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

    def components_for_entity(self, entity):
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

    def has_component(self, entity, component_type):
        """Check if a specific Entity has a Component of a certain type.

        :param entity: The Entity you are querying.
        :param component_type: The type of Component to check for.
        :return: True if the Entity has a Component of this type,
        otherwise False
        """
        return component_type in self._entities[entity]

    def add_component(self, entity, component_instance):
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

    def remove_component(self, entity, component_type):
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

        return entity

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

    def process(self, *args):
        """Call the process method on all Processors, in order of their priority.

        Call the *process* method on all assigned Processors, respecting their
        optional priority setting. In addition, any Entities that were marked
        for deletion since the last call to *World.process*, will be deleted
        at the start of this method call.

        :param args: Optional arguments that will be passed through to the
        *process* method of all Processors.
        """
        if self._dead_entities:
            for entity in self._dead_entities:
                self.delete_entity(entity, immediate=True)
            self._dead_entities.clear()

        for processor in self._processors:
            processor.process(*args)


class CachedWorld(World):
    def __init__(self, cache_size=128):
        """A sub-class of World using an LRU cache for Entity lookups."""
        super().__init__()
        self.set_cache_size(cache_size)

    def set_cache_size(self, size):
        """Set the maximum size of the LRU cache for Entity lookup.

        Replaces the existing cache.
        """
        wrapped = self._get_entities.__wrapped__.__get__(self, World)
        self._get_entities = lru_cache(size)(wrapped)

    def cache_clear(self):
        return self._get_entities.cache_clear()

    def cache_info(self):
        return self._get_entities.cache_info()

    def clear_database(self):
        """Remove all Entities and Components from the World."""
        super().clear_database()
        self.cache_clear()

    def delete_entity(self, entity, immediate=False):
        """Delete an Entity from the World."""
        if immediate:
            super().delete_entity(entity, immediate=True)
            self.cache_clear()
        else:
            self._dead_entities.add(entity)

    def add_component(self, entity, component_instance):
        """Add a new Component instance to an Entity."""
        super().add_component(entity, component_instance)
        self.cache_clear()

    def remove_component(self, entity, component_type):
        """Remove a Component instance from an Entity, by type."""
        super().remove_component(entity, component_type)
        self.cache_clear()

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
