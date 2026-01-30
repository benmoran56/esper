import pytest

import esper

from types import GeneratorType


# ECS test
@pytest.fixture(autouse=True)
def _reset_to_zero():
    # Wipe out all world contexts
    # and re-create the default.
    esper._context_map.clear()
    esper.switch_world("default")


def test_create_entity():
    entity1 = esper.create_entity()
    entity2 = esper.create_entity()
    assert isinstance(entity1, int)
    assert isinstance(entity2, int)
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


def test_get_entities():
    create_entities(100)
    generator = esper.get_entities()
    assert isinstance(generator, GeneratorType)
    assert isinstance(next(generator), int)
    assert len(list(generator)) == 99   # one already exhausted


def test_component_for_entity():
    entity = esper.create_entity(ComponentC())
    assert isinstance(esper.component_for_entity(entity, ComponentC), ComponentC)
    with pytest.raises(KeyError):
        esper.component_for_entity(entity, ComponentD)


def test_components_for_entity():
    entity = esper.create_entity(ComponentA(), ComponentD(), ComponentE())
    all_components: tuple[..., ...] = esper.components_for_entity(entity)
    assert isinstance(all_components, tuple)
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
        assert isinstance(ent, int)
        assert isinstance(comp, ComponentA)


def test_get_two_components():
    create_entities(2000)
    assert isinstance(esper.get_components(ComponentD, ComponentE), list)
    # Confirm that the actually contains something:
    assert len(esper.get_components(ComponentD, ComponentE)) > 0, "No Components Returned"

    for ent, comps in esper.get_components(ComponentD, ComponentE):
        assert isinstance(ent, int)
        assert isinstance(comps, tuple)
        assert len(comps) == 2

    for ent, (d, e) in esper.get_components(ComponentD, ComponentE):
        assert isinstance(ent, int)
        assert isinstance(d, ComponentD)
        assert isinstance(e, ComponentE)


def test_get_three_components():
    create_entities(2000)
    assert isinstance(esper.get_components(ComponentC, ComponentD, ComponentE), list)

    for ent, comps in esper.get_components(ComponentC, ComponentD, ComponentE):
        assert isinstance(ent, int)
        assert isinstance(comps, tuple)
        assert len(comps) == 3

    for ent, (c, d, e) in esper.get_components(ComponentC, ComponentD, ComponentE):
        assert isinstance(ent, int)
        assert isinstance(c, ComponentC)
        assert isinstance(d, ComponentD)
        assert isinstance(e, ComponentE)


def test_try_component():
    entity1 = esper.create_entity(ComponentA(), ComponentB())

    one_item = esper.try_component(entity=entity1, component_type=ComponentA)
    assert isinstance(one_item, ComponentA)

    zero_item = esper.try_component(entity=entity1, component_type=ComponentC)
    assert zero_item is None


def test_try_components():
    entity1 = esper.create_entity(ComponentA(), ComponentB())

    one_item = esper.try_components(entity1, ComponentA, ComponentB)
    assert isinstance(one_item, tuple)
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

    def test_try_remove_component(self):
        component_a = ComponentA()
        component_b = ComponentB()
        component_c = ComponentC()
        entity = esper.create_entity(component_a, component_b, component_c)

        # The component should be deleted the first time:
        _deleted_component = esper.try_remove_component(entity, ComponentB)
        assert _deleted_component is component_b
        assert not esper.has_component(entity, ComponentB)

        # Future calls should return None, and not raise any Exception:
        _deleted_component = esper.try_remove_component(entity, ComponentB)
        assert _deleted_component is None


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
    # The `create_entities` helper will add <number>/2 of
    # 'ComponentA' to the World context. Make a new
    # "left" context, and confirm this is True:
    esper.switch_world("left")
    assert len(esper.get_component(ComponentA)) == 0
    create_entities(200)
    assert len(esper.get_component(ComponentA)) == 100

    # Switching to a new "right" World context, no
    # 'ComponentA' Components should yet exist.
    esper.switch_world("right")
    assert len(esper.get_component(ComponentA)) == 0
    create_entities(300)
    assert len(esper.get_component(ComponentA)) == 150

    # Switching back to the original "left" context,
    # the original 100 Components should still exist.
    # From there, 200 more should be added:
    esper.switch_world("left")
    assert len(esper.get_component(ComponentA)) == 100
    create_entities(400)
    assert len(esper.get_component(ComponentA)) == 300


##################################################
#   Some helper functions and Component templates:
##################################################
def create_entities(number):
    """This function will create X number of entities.

    The entities are created with a mix of Components,
    so the World context will see an addition of
    ComponentA * number * 1
    ComponentB * number * 1
    ComponentC * number * 2
    ComponentD * number * 1
    ComponentE * number * 1
    """
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


# Processor test
def test_add_processor():
    create_entities(2000)
    assert len(esper._processors) == 0
    correct_processor_a = CorrectProcessorA()
    assert isinstance(correct_processor_a, esper.Processor)
    esper.add_processor(correct_processor_a)
    assert len(esper._processors) == 1
    assert isinstance(esper._processors[0], esper.Processor)


def test_remove_processor():
    create_entities(2000)
    assert len(esper._processors) == 0
    correct_processor_a = CorrectProcessorA()
    esper.add_processor(correct_processor_a)
    assert len(esper._processors) == 1
    esper.remove_processor(CorrectProcessorB)
    assert len(esper._processors) == 1
    esper.remove_processor(CorrectProcessorA)
    assert len(esper._processors) == 0


def test_get_processor():
    processor_a = CorrectProcessorA()
    processor_b = CorrectProcessorB()
    processor_c = CorrectProcessorC()

    esper.add_processor(processor_a)
    esper.add_processor(processor_b)
    esper.add_processor(processor_c)

    retrieved_proc_c = esper.get_processor(CorrectProcessorC)
    retrieved_proc_b = esper.get_processor(CorrectProcessorB)
    retrieved_proc_a = esper.get_processor(CorrectProcessorA)
    assert type(retrieved_proc_a) == CorrectProcessorA
    assert type(retrieved_proc_b) == CorrectProcessorB
    assert type(retrieved_proc_c) == CorrectProcessorC


def test_processor_args():
    esper.add_processor(ArgsProcessor())
    with pytest.raises(TypeError):
        esper.process()  # Missing argument
    esper.process("arg")


def test_processor_kwargs():
    esper.add_processor(KwargsProcessor())
    with pytest.raises(TypeError):
        esper.process()  # Missing argument
    esper.process("spam", "eggs")
    esper.process("spam", eggs="eggs")
    esper.process(spam="spam", eggs="eggs")
    esper.process(eggs="eggs", spam="spam")


# Event dispatch test
def test_event_dispatch_no_handlers():
    esper.dispatch_event("foo")
    esper.dispatch_event("foo", 1)
    esper.dispatch_event("foo", 1, 2)
    esper.event_registry.clear()


def test_event_dispatch_one_arg():
    esper.set_handler("foo", myhandler_onearg)
    esper.dispatch_event("foo", 1)
    esper.event_registry.clear()


def test_event_dispatch_two_args():
    esper.set_handler("foo", myhandler_twoargs)
    esper.dispatch_event("foo", 1, 2)
    esper.event_registry.clear()


def test_event_dispatch_incorrect_args():
    esper.set_handler("foo", myhandler_noargs)
    with pytest.raises(TypeError):
        esper.dispatch_event("foo", "arg1", "arg2")
    esper.event_registry.clear()


def test_set_methoad_as_handler_in_init():

    class MyClass(esper.Processor):

        def __init__(self):
            esper.set_handler("foo", self._my_handler)

        @staticmethod
        def _my_handler():
            print("OK")

        def process(self, dt):
            pass

    _myclass = MyClass()
    esper.dispatch_event("foo")
    esper.event_registry.clear()


def test_set_instance_methoad_as_handler():
    class MyClass(esper.Processor):

        @staticmethod
        def my_handler():
            print("OK")

        def process(self, dt):
            pass

    myclass = MyClass()
    esper.set_handler("foo", myclass.my_handler)
    esper.dispatch_event("foo")
    esper.event_registry.clear()


def test_event_handler_switch_world():
    called = 0
    def handler():
        nonlocal called
        called += 1

    # Switch to a new "left" World context, and register
    # an event handler. Confirm that it is being called
    # by checking that the 'called' variable is incremented.
    esper.switch_world("left")
    esper.set_handler("foo", handler)
    assert called == 0
    esper.dispatch_event("foo")
    assert called == 1

    # Here we switch to a new "right" World context.
    # The handler is registered to the "left" context only,
    # so dispatching the event should have no effect. The
    # handler is not attached, and so the 'called' value
    # should not be incremented further.
    esper.switch_world("right")
    esper.dispatch_event("foo")
    assert called == 1

    # Switching back to the "left" context and dispatching
    # the event, the handler should still be registered and
    # the 'called' variable should be incremented by 1.
    esper.switch_world("left")
    esper.dispatch_event("foo")
    assert called == 2

def test_remove_handler():
    def handler():
        pass

    assert esper.event_registry == {}
    esper.set_handler("foo", handler)
    assert "foo" in esper.event_registry
    esper.remove_handler("foo", handler)
    assert esper.event_registry == {}


##################################################
#             Advanced Feature Tests             #
##################################################


def test_delayed_delete_entity():
    """
    Verify that delayed entity deletion works as expected.

    This test checks the default deletion behavior (`immediate=False`).
    It ensures that:
    1. An entity marked for deletion is immediately considered non-existent
       by the public `entity_exists()` function.
    2. The entity's data, however, remains in the internal database
       structures until the cleanup process is run.
    3. After `clear_dead_entities()` is called, the entity is completely
       purged from the database.
    """
    entity = esper.create_entity(ComponentA())
    esper.delete_entity(entity, immediate=False)

    assert esper.entity_exists(entity) is False
    assert entity in esper._entities

    esper.clear_dead_entities()

    assert entity not in esper._entities
    with pytest.raises(KeyError):
        esper.components_for_entity(entity)


def test_cache_invalidation_on_add_component():
    """
    Verify that adding a component correctly invalidates the query cache.

    This test ensures that:
    1. A query is run to populate the cache (making it "hot").
    2. A new component is added to an existing entity, which should trigger
       the lazy cache invalidation mechanism by setting the dirty flag.
    3. A subsequent query correctly rebuilds the cache and returns the
       expected results.
    """
    entity = esper.create_entity(ComponentA())

    result1 = esper.get_component(ComponentA)
    assert len(result1) == 1

    esper.add_component(entity, ComponentB())

    esper.clear_cache()
    result2 = esper.get_component(ComponentA)
    assert len(result2) == 1


def test_cache_invalidation_on_remove_component():
    """
    Verify that removing a component correctly invalidates the query cache.

    This test ensures that:
    1. A query for a specific component combination is run to populate the cache.
    2. One of the components is removed from the entity, which should
       trigger the lazy cache invalidation by setting the dirty flag.
    3. A subsequent query for the same component combination correctly
       returns an empty result and clears the dirty flag.
    """
    entity = esper.create_entity(ComponentA(), ComponentB())

    result1 = esper.get_components(ComponentA, ComponentB)
    assert len(result1) == 1

    esper.remove_component(entity, ComponentB)

    result2 = esper.get_components(ComponentA, ComponentB)
    assert len(result2) == 0


def test_processor_priority():
    """
    Verify that processors are executed in the correct order based on priority.

    This test adds two processors, A and B, with different priority values
    (A has a higher priority of 10, B has a lower priority of 5). It then
    confirms that when `esper.process()` is called, the processor with the
    higher numerical priority (Processor A) is executed before the one with
    the lower priority.
    """

    class PriorityProcessorA(esper.Processor):
        priority = 10

        def process(self, order_list):
            order_list.append('A')

    class PriorityProcessorB(esper.Processor):
        priority = 5

        def process(self, order_list):
            order_list.append('B')

    proc_b = PriorityProcessorB()
    proc_a = PriorityProcessorA()

    esper.add_processor(proc_b, priority=proc_b.priority)
    esper.add_processor(proc_a, priority=proc_a.priority)

    order = []
    esper.process(order)

    assert order == ['A', 'B']


def test_weak_reference_handler_removal():
    """
    Verify that event handlers are automatically unregistered when garbage collected.

    The event system uses weak references to handlers to prevent memory leaks.
    This test confirms that:
    1. A method from a temporary object instance is registered as an event handler.
    2. After the only strong reference to the instance is deleted, the garbage
       collector reclaims the object.
    3. The weak reference in the event registry becomes dead, and the handler
       is automatically removed via its callback.
    4. Dispatching the event no longer calls the handler, and the event name
       is removed from the registry.
    """
    called = 0

    class TempHandler:
        def handle(self):
            nonlocal called
            called += 1

    temp_instance = TempHandler()
    esper.set_handler("temp_event", temp_instance.handle)

    assert "temp_event" in esper.event_registry

    del temp_instance

    import gc
    gc.collect()

    esper.dispatch_event("temp_event")
    assert called == 0

    assert "temp_event" not in esper.event_registry


def test_delete_world():
    """
    Verify the functionality of creating and deleting world contexts.

    This test checks that:
    1. A new world context can be created implicitly via `switch_world`.
    2. The `list_worlds` function correctly reports the existence of the new world.
    3. The `delete_world` function successfully removes the specified world.
    4. Attempting to delete a non-existent world correctly raises a KeyError.
    """
    esper.switch_world("temp_world")
    esper.switch_world("default")

    assert "temp_world" in esper.list_worlds()
    esper.delete_world("temp_world")
    assert "temp_world" not in esper.list_worlds()

    with pytest.raises(KeyError):
         esper.delete_world("non_existent")

##################################################
#   Some helper functions and Component templates:
##################################################
class CorrectProcessorA(esper.Processor):

    def process(self):
        pass


class CorrectProcessorB(esper.Processor):
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def process(self):
        pass


class CorrectProcessorC(esper.Processor):

    def process(self):
        pass


class ArgsProcessor(esper.Processor):

    def process(self, spam):
        pass


class KwargsProcessor(esper.Processor):
    def process(self, spam, eggs):
        pass


class IncorrectProcessor:

    def process(self):
        pass


# Event handler templates:

def myhandler_noargs():
    print("OK")


def myhandler_onearg(arg):
    print("Arg:", arg)


def myhandler_twoargs(arg1, arg2):
    print("Args:", arg1, arg2)
