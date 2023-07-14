import pytest
import esper


@pytest.fixture(autouse=True)
def _clear_database():
    esper.clear_database()


def test_create_entity():
    entity1 = esper.create_entity()
    entity2 = esper.create_entity()
    assert type(entity1) == int
    assert type(entity2) == int
    assert entity1 < entity2


def test_create_entity_with_components():
    entity1 = esper.create_entity(ComponentA())
    entity2 = esper.create_entity(ComponentB(), ComponentC())
    assert esper.has_component(entity1, ComponentA) is True
    assert esper.has_component(entity1, ComponentB) is False
    assert esper.has_component(entity1, ComponentC) is False
    assert esper.has_component(entity2, ComponentA) is False
    assert esper.has_component(entity2, ComponentB) is True
    assert esper.has_component(entity2, ComponentC) is True


def test_adding_component_to_not_existing_entity_raises_error():
    with pytest.raises(KeyError):
        esper.add_component(123, ComponentA())


def test_create_entity_and_add_components():
    entity1 = esper.create_entity()
    esper.add_component(entity1, ComponentA())
    esper.add_component(entity1, ComponentB())
    assert esper.has_component(entity1, ComponentA) is True
    assert esper.has_component(entity1, ComponentC) is False


def test_create_entity_and_add_components_with_alias():
    entity = esper.create_entity()
    esper.add_component(entity, ComponentA(), type_alias=ComponentF)
    assert esper.has_component(entity, ComponentF) is True
    assert esper.component_for_entity(entity, ComponentF).a == -66  # type: ignore[attr-defined]


def test_delete_entity():
    esper.create_entity(ComponentA())
    entity_b = esper.create_entity(ComponentB())
    entity_c = esper.create_entity(ComponentC())
    empty_entity = esper.create_entity()
    assert entity_c == 3
    esper.delete_entity(entity_b, immediate=True)
    with pytest.raises(KeyError):
        esper.components_for_entity(entity_b)
    with pytest.raises(KeyError):
        esper.delete_entity(999, immediate=True)
    esper.delete_entity(empty_entity, immediate=True)


def test_component_for_entity():
    entity = esper.create_entity(ComponentC())
    assert isinstance(esper.component_for_entity(entity, ComponentC), ComponentC)
    with pytest.raises(KeyError):
        esper.component_for_entity(entity, ComponentD)


def test_components_for_entity():
    entity = esper.create_entity(ComponentA(), ComponentD(), ComponentE())
    all_components: tuple[..., ...] = esper.components_for_entity(entity)
    assert type(all_components) == tuple
    assert len(all_components) == 3
    with pytest.raises(KeyError):
        esper.components_for_entity(999)


def test_has_component():
    entity1 = esper.create_entity(ComponentA())
    entity2 = esper.create_entity(ComponentB())
    assert esper.has_component(entity1, ComponentA) is True
    assert esper.has_component(entity1, ComponentB) is False
    assert esper.has_component(entity2, ComponentA) is False
    assert esper.has_component(entity2, ComponentB) is True


def test_has_components():
    entity = esper.create_entity(ComponentA(), ComponentB(), ComponentC())
    assert esper.has_components(entity, ComponentA, ComponentB) is True
    assert esper.has_components(entity, ComponentB, ComponentC) is True
    assert esper.has_components(entity, ComponentA, ComponentC) is True
    assert esper.has_components(entity, ComponentA, ComponentD) is False
    assert esper.has_components(entity, ComponentD) is False


def test_get_component():
    create_entities(2000)
    assert isinstance(esper.get_component(ComponentA), list)
    # Confirm that the actually contains something:
    assert len(esper.get_component(ComponentA)) > 0, "No Components Returned"

    for ent, comp in esper.get_component(ComponentA):
        assert type(ent) == int
        assert type(comp) == ComponentA


def test_get_two_components():
    create_entities(2000)
    assert isinstance(esper.get_components(ComponentD, ComponentE), list)
    # Confirm that the actually contains something:
    assert len(esper.get_components(ComponentD, ComponentE)) > 0, "No Components Returned"

    for ent, comps in esper.get_components(ComponentD, ComponentE):
        assert type(ent) == int
        assert type(comps) == list
        assert len(comps) == 2

    for ent, (d, e) in esper.get_components(ComponentD, ComponentE):
        assert type(ent) == int
        assert type(d) == ComponentD
        assert type(e) == ComponentE


def test_get_three_components():
    create_entities(2000)
    assert isinstance(esper.get_components(ComponentC, ComponentD, ComponentE), list)

    for ent, comps in esper.get_components(ComponentC, ComponentD, ComponentE):
        assert type(ent) == int
        assert type(comps) == list
        assert len(comps) == 3

    for ent, (c, d, e) in esper.get_components(ComponentC, ComponentD, ComponentE):
        assert type(ent) == int
        assert type(c) == ComponentC
        assert type(d) == ComponentD
        assert type(e) == ComponentE


def test_try_component():
    entity1 = esper.create_entity(ComponentA(), ComponentB())

    one_item = esper.try_component(entity=entity1, component_type=ComponentA)
    assert isinstance(one_item, ComponentA)

    zero_item = esper.try_component(entity=entity1, component_type=ComponentC)
    assert zero_item is None


def test_try_components():
    entity1 = esper.create_entity(ComponentA(), ComponentB())

    one_item = esper.try_components(entity1, ComponentA, ComponentB)
    assert isinstance(one_item, list)
    assert len(one_item) == 2
    assert isinstance(one_item[0], ComponentA)
    assert isinstance(one_item[1], ComponentB)

    zero_item = esper.try_components(entity1, ComponentA, ComponentC)
    assert zero_item is None


def test_clear_database():
    create_entities(2000)
    assert len(esper.get_component(ComponentA)) == 1000
    esper.clear_database()
    assert len(esper.get_component(ComponentA)) == 0


def test_clear_cache():
    create_entities(2000)
    assert len(esper.get_component(ComponentA)) == 1000
    esper.clear_cache()
    assert len(esper.get_component(ComponentA)) == 1000


def test_cache_results():
    _______ = esper.create_entity(ComponentA(), ComponentB(), ComponentC())
    entity2 = esper.create_entity(ComponentB(), ComponentC(), ComponentD())
    assert len(esper.get_components(ComponentB, ComponentC)) == 2
    esper.delete_entity(entity2, immediate=True)
    assert len(esper.get_components(ComponentB, ComponentC)) == 1


class TestEntityExists:
    def test_dead_entity(self):
        dead_entity = esper.create_entity(ComponentB())
        esper.delete_entity(dead_entity)
        assert not esper.entity_exists(dead_entity)

    def test_not_created_entity(self):
        assert not esper.entity_exists(123)

    def test_empty_entity(self):
        empty_entity = esper.create_entity()
        assert esper.entity_exists(empty_entity)

    def test_entity_with_component(self):
        entity_with_component = esper.create_entity(ComponentA())
        assert esper.entity_exists(entity_with_component)


class TestRemoveComponent:
    def test_remove_from_not_existing_entity_raises_key_error(self):
        with pytest.raises(KeyError):
            esper.remove_component(123, ComponentA)

    def test_remove_not_existing_component_raises_key_error(self):
        entity = esper.create_entity(ComponentB())

        with pytest.raises(KeyError):
            esper.remove_component(entity, ComponentA)

    def test_remove_component_with_object_raises_key_error(self):
        create_entities(2000)
        entity = 2
        component = ComponentD()

        assert esper.has_component(entity, type(component))
        with pytest.raises(KeyError):
            esper.remove_component(entity, component)  # type: ignore[arg-type]

    def test_remove_component_returns_removed_instance(self):
        component = ComponentA()
        entity = esper.create_entity(component)

        result = esper.remove_component(entity, type(component))

        assert result is component

    def test_remove_last_component_leaves_empty_entity(self):
        entity = esper.create_entity()
        esper.add_component(entity, ComponentA())

        esper.remove_component(entity, ComponentA)

        assert not esper.has_component(entity, ComponentA)
        assert esper.entity_exists(entity)

    def test_removing_one_component_leaves_other_intact(self):
        component_a = ComponentA()
        component_b = ComponentB()
        component_c = ComponentC()
        entity = esper.create_entity(component_a, component_b, component_c)

        esper.remove_component(entity, ComponentB)

        assert esper.component_for_entity(entity, ComponentA) is component_a
        assert not esper.has_component(entity, ComponentB)
        assert esper.component_for_entity(entity, ComponentC) is component_c


def test_clear_dead_entities():
    component = ComponentA()
    entity1 = esper.create_entity(component)
    entity2 = esper.create_entity()
    assert esper.entity_exists(entity1)
    assert esper.entity_exists(entity2)
    assert esper.has_component(entity1, ComponentA)
    esper.delete_entity(entity1, immediate=False)
    assert not esper.entity_exists(entity1)
    assert esper.entity_exists(entity2)
    assert esper.has_component(entity1, ComponentA)
    esper.clear_dead_entities()
    assert not esper.entity_exists(entity1)
    assert esper.entity_exists(entity2)
    with pytest.raises(KeyError):
        assert esper.has_component(entity1, ComponentA)


def test_switch_world():
    esper.init_world("left")
    esper.init_world("right")
    esper.switch_world("left")
    assert len(esper.get_component(ComponentA)) == 0
    create_entities(200)
    assert len(esper.get_component(ComponentA)) == 100
    esper.switch_world("right")
    assert len(esper.get_component(ComponentA)) == 0
    create_entities(300)
    assert len(esper.get_component(ComponentA)) == 150
    esper.switch_world("left")
    assert len(esper.get_component(ComponentA)) == 100
    create_entities(400)
    assert len(esper.get_component(ComponentA)) == 300


##################################################
#   Some helper functions and Component templates:
##################################################
def create_entities(number):
    for _ in range(number // 2):
        esper.create_entity(ComponentA(), ComponentB(), ComponentC())
        esper.create_entity(ComponentC(), ComponentD(), ComponentE())


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


class ComponentF:
    pass
