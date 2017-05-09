import esper
import types
import pytest


@pytest.fixture
def world():
    return esper.CachedWorld()


@pytest.fixture
def populated_world():
    pop_world = esper.CachedWorld()
    create_entities(pop_world, 2000)
    return pop_world


def test_world_instantiation(world):
    assert type(world) == esper.CachedWorld
    assert type(world._next_entity_id) == int
    assert type(world._entities) == dict
    assert type(world._components) == dict
    assert type(world._processors) == list


def test_create_entity(world):
    entity1 = world.create_entity()
    entity2 = world.create_entity()
    assert type(entity1) and type(entity2) == int
    assert entity1 < entity2


def test_create_entity_with_components(world):
    entity1 = world.create_entity(ComponentA())
    entity2 = world.create_entity(ComponentB())
    assert world.has_component(entity1, ComponentA) is True
    assert world.has_component(entity1, ComponentB) is False
    assert world.has_component(entity2, ComponentA) is False
    assert world.has_component(entity2, ComponentB) is True


def test_delete_entity(world):
    # TODO: handle case where entity has never been assigned components
    entity1 = world.create_entity()
    world.add_component(entity1, ComponentC())
    entity2 = world.create_entity()
    world.add_component(entity2, ComponentD())
    entity3 = world.create_entity()
    world.add_component(entity3, ComponentE())

    assert entity3 == 3
    world.delete_entity(entity3, immediate=True)
    with pytest.raises(KeyError):
        world.components_for_entity(entity3)
    with pytest.raises(KeyError):
        world.delete_entity(999, immediate=True)


def test_component_for_entity(world):
    entity = world.create_entity()
    world.add_component(entity, ComponentC())
    assert isinstance(world.component_for_entity(entity, ComponentC), ComponentC)
    with pytest.raises(KeyError):
        world.component_for_entity(entity, ComponentD)


def test_components_for_entity(world):
    entity = world.create_entity()
    world.add_component(entity, ComponentA())
    world.add_component(entity, ComponentD())
    world.add_component(entity, ComponentE())
    all_components = world.components_for_entity(entity)
    assert type(all_components) == tuple
    assert len(all_components) == 3
    with pytest.raises(KeyError):
        world.components_for_entity(999)


def test_has_component(world):
    entity1 = world.create_entity()
    entity2 = world.create_entity()
    world.add_component(entity1, ComponentA())
    world.add_component(entity2, ComponentB())
    assert world.has_component(entity1, ComponentA) is True
    assert world.has_component(entity1, ComponentB) is False
    assert world.has_component(entity2, ComponentA) is False
    assert world.has_component(entity2, ComponentB) is True


def test_get_component(populated_world):
    assert isinstance(populated_world.get_component(ComponentA), list)

    for ent, comp in populated_world.get_component(ComponentA):
        assert type(ent) == int
        assert type(comp) == ComponentA


def test_get_two_components(populated_world):
    assert isinstance(populated_world.get_components(ComponentD, ComponentE), list)

    for ent, comps in populated_world.get_components(ComponentD, ComponentE):
        assert type(ent) == int
        assert type(comps) == list
        assert len(comps) == 2

    for ent, (d, e) in populated_world.get_components(ComponentD, ComponentE):
        assert type(ent) == int
        assert type(d) == ComponentD
        assert type(e) == ComponentE


def test_get_three_components(populated_world):
    assert isinstance(populated_world.get_components(ComponentC, ComponentD, ComponentE), list)

    for ent, comps in populated_world.get_components(ComponentC, ComponentD, ComponentE):
        assert type(ent) == int
        assert type(comps) == list
        assert len(comps) == 3

    for ent, (c, d, e) in populated_world.get_components(ComponentC, ComponentD, ComponentE):
        assert type(ent) == int
        assert type(c) == ComponentC
        assert type(d) == ComponentD
        assert type(e) == ComponentE


def test_clear_database(populated_world):
    populated_world.clear_database()
    assert len(populated_world._entities) == 0
    assert len(populated_world._components) == 0
    assert len(populated_world._processors) == 0
    assert populated_world._next_entity_id == 0


def test_add_processor(populated_world):
    assert len(populated_world._processors) == 0
    correct_processor_a = CorrectProcessorA()
    assert isinstance(correct_processor_a, esper.Processor)
    populated_world.add_processor(correct_processor_a)
    assert len(populated_world._processors) == 1
    assert isinstance(populated_world._processors[0], esper.Processor)


def test_remove_processor(populated_world):
    assert len(populated_world._processors) == 0
    correct_processor_a = CorrectProcessorA()
    populated_world.add_processor(correct_processor_a)
    assert len(populated_world._processors) == 1
    populated_world.remove_processor(CorrectProcessorB)
    assert len(populated_world._processors) == 1
    populated_world.remove_processor(CorrectProcessorA)
    assert len(populated_world._processors) == 0


def test_get_processor(world):
    processor_a = CorrectProcessorA()
    processor_b = CorrectProcessorB()
    world.add_processor(processor_a)
    world.add_processor(processor_b)
    retrieved_proc_b = world.get_processor(CorrectProcessorB)
    retrieved_proc_a = world.get_processor(CorrectProcessorA)
    assert type(retrieved_proc_a) == CorrectProcessorA
    assert type(retrieved_proc_b) == CorrectProcessorB


##################################################
#   Some helper functions and Component templates:
##################################################
def create_entities(world, number):
    for _ in range(number // 2):
        enemy_type_a = world.create_entity()
        world.add_component(enemy_type_a, ComponentA())
        world.add_component(enemy_type_a, ComponentB())
        world.add_component(enemy_type_a, ComponentD())
        world.add_component(enemy_type_a, ComponentE())
        enemy_type_b = world.create_entity()
        world.add_component(enemy_type_b, ComponentC())
        world.add_component(enemy_type_b, ComponentD())
        world.add_component(enemy_type_b, ComponentE())


class ComponentA:
    def __init__(self):
        self.a = -66
        self.b = 9999.99


class ComponentB:
    def __init__(self):
        self.attrib_a = True
        self.attrib_b = False
        self.attrib_c = False
        self.attrib_d = True


class ComponentC:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.z = None


class ComponentD:
    def __init__(self):
        self.direction = "left"
        self.previous = "right"


class ComponentE:
    def __init__(self):
        self.items = {"itema": None, "itemb": 1000}
        self.points = [a + 2 for a in list(range(44))]


class CorrectProcessorA(esper.Processor):
    def __init__(self):
        super().__init__()

    def process(self):
        pass


class CorrectProcessorB(esper.Processor):
    def __init__(self):
        super().__init__()

    def process(self):
        pass


class IncorrectProcessor:
    def __init__(self):
        super().__init__()

    def process(self):
        pass
