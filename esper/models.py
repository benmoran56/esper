

class Component:
    """All components should inherrit from this class."""
    pass


class System:
    def __init__(self):
        self.world = None

    def process(self):
        raise NotImplementedError
