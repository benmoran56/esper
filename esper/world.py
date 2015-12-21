

class World:
    def __init__(self):
        """A World object, which holds references to all Systems and Entities.

        A World keeps track of all entities and their related components. It
        also calls the process method on any Systems assigned to it.
        """
        self._systems = []
        self._next_entity_id = 0
        self._database = {}

    def add_system(self, system_instance, priority=0):
        """Add a System instance to the world.

        :param system_instance: An instance of a System subclassed from the System class
        :param priority: The processing order for the System, with smaller
        numbers being a higher priority. For example, 2 is processed before 5.
        """
        system_instance.priority = priority
        system_instance.world = self
        self._systems.append(system_instance)
        self._systems.sort(key=lambda s: s.priority)

    def delete_system(self, system):
        """Delete a system from the World.

        :param system: The System instance you wish to delete.
        """
        self._systems.remove(system)

    def create_entity(self):
        """Create a new entity.

        This method return an entity ID, which is just a simple integer.
        :return: The next entity ID in sequence.
        """
        self._next_entity_id += 1
        return self._next_entity_id

    def add_component(self, entity, component_instance):
        component_type = type(component_instance)
        if entity not in self._database:
            self._database[entity] = {component_type: component_instance}
        else:
            self._database[entity][component_type] = component_instance
        # TODO: raise an exception if the component type already exists

    def remove_component(self):
        pass

    def process(self):
        """Process all Systems, in order of their priority."""
        for system in self._systems:
            system.process()

