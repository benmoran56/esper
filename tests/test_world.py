import esper
import pytest


@pytest.fixture
def world():
    return esper.World()


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

