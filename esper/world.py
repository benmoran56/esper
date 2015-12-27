

class World:
    def __init__(self):
        """A World object, which holds references to all Entities and Processors.

        A World keeps track of all entities and their related components. It
        also handles calling the process method on any Processors assigned to it.
        """
        self._processors = []
        self._next_entity_id = 0
        self._database = {}

    def add_processor(self, processor_instance, priority=0):
        """Add a Processor instance to the world.

        :param processor_instance: An instance of a Processor,
        subclassed from the Processor class
        :param priority: The processing order for the Processor, with smaller
        numbers being a higher priority. For example: 2 is processed before 5.
        """
        processor_instance.priority = priority
        processor_instance.world = self
        self._processors.append(processor_instance)
        self._processors.sort(key=lambda processor: processor.priority)

    def remove_processor_instance(self, processor_instance):
        """Remove a Processor instance from the World.

        :param processor_instance: The Processor instance you wish to remove.
        """
        try:
            processor_instance.world = None
            self._processors.remove(processor_instance)
        except ValueError:
            pass

    def remove_processor(self, processor_type):
        """Remove a Processor from the world, by type.

        :param processor_type: The class type of the Processor to remove.
        """
        for processor in self._processors:
            if type(processor) == processor_type:
                processor.world = None
                self._processors.remove(processor)

    def create_entity(self):
        """Create a new entity.

        This method return an entity ID, which is just a simple integer.
        :return: The next entity ID in sequence.
        """
        self._next_entity_id += 1
        return self._next_entity_id

    def delete_entity(self, entity):
        """Delete an entity from the World.

        Delete an entity from the World. This will also delete any Components
        that are assigned to the entity.
        :param entity: The entity ID you wish to delete.
        """
        try:
            del self._database[entity]
        except KeyError:
            pass

    def add_component(self, entity, component_instance):
        """Add a new Component instance to an Entity.

        :param entity: The Entity to associate the Component with.
        :param component_instance: A Component instance.
        """
        component_type = type(component_instance)
        if entity not in self._database:
            self._database[entity] = {}
        self._database[entity][component_type] = component_instance

    def remove_component(self, entity, component_type):
        """Remove a Component from an Entity, by type.

        An Component instance can be removed from an Entity by
        providing it's type.
        For example: remove_component(player, Velocity) will remove
        the Velocity instance from the player Entity.

        :param entity: The Entity to remove the Component from.
        :param component_type: The type of the Component to remove.
        """
        try:
            del self._database[entity][component_type]
        except KeyError:
            pass

    def get_component(self, component_type):
        """Get an iterator for entity, Component pairs.

        :param component_type: The Component type to retrieve.
        :return: An iterator for (Entity, Component) tuples.
        """
        database = self._database
        try:
            for entity in database:
                yield entity, database[entity][component_type]
        except KeyError:
            pass

    def get_components(self, *component_types):
        """Get an iterator for entity and multiple Component sets.

        :param component_types: Two or more Component types.
        :return: An iterator for (Entity, Component1, Component2, etc)
        tuples.
        """
        database = self._database
        try:
            for entity in database:
                yield entity, [database[entity][ct] for ct in component_types]
        except KeyError:
            pass

    def process(self):
        """Process all Systems, in order of their priority."""
        for processor in self._processors:
            processor.process()
