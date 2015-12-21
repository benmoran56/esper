class World:
    def __init__(self):
        """A World object, which holds references to all Systems and Entities.

        """
        # TODO: proper docstring
        self._systems = []
        self._next_entity_id = -1

    def add_system(self, system, priority=0):
        """Add a System to the world

        :param system: An instance of a System which has inherrited from
        the System
        :param priority:
        """
        # TODO: set the system's self.world parameter.
        system._priority = priority
        self._systems.append(system)
        self._systems.sort(key=lambda x: x.priority)

    def delete_system(self, system):
        """Delete a system from the World.

        :param system: The System instance you wish to delete.
        """
        self._systems.remove(system)

    def create_entity(self):
        """Create a new entity.

        This method return an entity ID, which is simply an integer.
        :return: The next entity ID in sequence.
        """
        self._next_entity_id += 1
        return self._next_entity_id

    def process(self):
        """Process all Systems, in order of priority."""
        for system in self._systems:
            system.process()


class Component(object):
    """All components should inherrit from this class."""
    pass


class System:
    def __init__(self):
        self._priority = 0
        self.world = None

    def process(self):
        raise NotImplementedError
