import esper

import types
import pytest


@pytest.fixture
def world():
    return esper.World()


@pytest.fixture
def populated_world():
    pop_world = esper.World()
    create_entities(pop_world, 2000)
    return pop_world


def test_world_instantiation(world):
    assert type(world) == esper.World
    assert type(world._next_entity_id) == int
    assert type(world._entities) == dict
    assert type(world._components) == dict
    assert type(world._processors) == list


def test_entity_creation(world):
    entity1 = world.create_entity()
    entity2 = world.create_entity()
    assert type(entity1) and type(entity2) == int
    assert entity1 < entity2


def test_single_component_query(populated_world):
    assert isinstance(populated_world.get_component(ComponentA), types.GeneratorType)

    for ent, comp in populated_world.get_component(ComponentA):
        assert type(ent) == int
        assert type(comp) == ComponentA


def test_dual_component_query(populated_world):
    assert isinstance(populated_world.get_components(ComponentD, ComponentE),
                      types.GeneratorType)

    for ent, comps in populated_world.get_components(ComponentD, ComponentE):
        assert type(ent) == int
        assert type(comps) == list
        assert len(comps) == 2

    for ent, (d, e) in populated_world.get_components(ComponentD, ComponentE):
        assert type(ent) == int
        assert type(d) == ComponentD
        assert type(e) == ComponentE


def test_triple_component_query(populated_world):
    assert isinstance(populated_world.get_components(ComponentC, ComponentD, ComponentE),
                      types.GeneratorType)

    for ent, comps in populated_world.get_components(ComponentC, ComponentD, ComponentE):
        assert type(ent) == int
        assert type(comps) == list
        assert len(comps) == 3

    for ent, (c, d, e) in populated_world.get_components(ComponentC, ComponentD, ComponentE):
        assert type(ent) == int
        assert type(c) == ComponentC
        assert type(d) == ComponentD
        assert type(e) == ComponentE


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
