

class World:
    def __init__(self):
        """A World object keeps track of all Entities, Components and Processors.

        A World contains a database of all Entity/Component assignments. It also
        handles calling the process method on any Processors assigned to it.
        """
        self._processors = []
        self._next_entity_id = 0
        self._database = {}

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
        try:
            del self._database[entity]
        except KeyError:
            pass

    def component_for_entity(self, entity, component_type):
        """Retrieve a specific Component instance for an Entity.

        :param entity: The Entity to retrieve the Component for.
        :param component_type: The Component instance you wish to retrieve.
        :return: A Component instance, *if* it exists for the Entity.
        """
        try:
            return self._database[entity][component_type]
        except KeyError:
            pass

    def add_component(self, entity, component_instance):
        """Add a new Component instance to an Entity.

        If a Component of the same type is already assigned to the Entity,
        it will be replaced with the new one.
        :param entity: The Entity to associate the Component with.
        :param component_instance: A Component instance.
        """
        component_type = type(component_instance)
        if entity not in self._database:
            self._database[entity] = {}
        self._database[entity][component_type] = component_instance

    def delete_component(self, entity, component_type):
        """Delete a Component instance from an Entity, by type.

        An Component instance can be Deleted by providing it's type.
        For example: world.delete_component(enemy_a, Velocity) will remove
        the Velocity instance from the Entity enemy_a.

        :param entity: The Entity to delete the Component from.
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
        for entity in database:
            try:
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
        for entity in database:
            try:
                yield entity, [database[entity][ct] for ct in component_types]
            except KeyError:
                pass

    def process(self):
        """Process all Systems, in order of their priority."""
        for processor in self._processors:
            processor.process()
