"""
check a one-to-many relationship implementation is working
this test suite implementation uses the theme of ownership
"""

import esper


class Inventory:
    """the entity belongs to the inventory
    every entity in the same group must use the same instance of Inventory"""


class Hold:
    """the inventory belongs to this entity"""

    def __init__(self, invent: Inventory) -> None:
        self.invent = invent


def test_query_owned() -> None:
    invent = Inventory()

    owner = esper.create_entity(Hold(invent))
    expected = [esper.create_entity(invent), esper.create_entity(invent)]

    esper.create_entity(Inventory())

    # we want to get all owned entities by owner
    # step 1 : get Hold component of $owner
    h = esper.try_component(owner, Hold)
    assert h is not None
    # step 2 : iterates entities with an Inventory component
    result = []
    for owned, invent in esper.get_component(Inventory):
        # step 3 : skip the entities with another Inventory
        if invent is not h.invent:
            continue
        # we would get entities owned by $owner
        result.append(owned)

    # check result
    assert result == expected


def test_get_owner() -> None:
    invent = Inventory()

    expected = [esper.create_entity(Hold(invent))]
    owned = esper.create_entity(invent)

    esper.create_entity(Hold(Inventory()))

    # we want to get the owner of $owned
    # step 1 : get Inventory component of $owned
    invent_ = esper.try_component(owned, Inventory)
    assert invent_ is not None
    # step 2 : iterates entities with a Hold component
    result = []
    for owner, h in esper.get_component(Hold):
        # step 3 : skip entities that own an other Inventory
        if h.invent is not invent_:
            continue
        # we would get the entity that owns $owned
        result.append(owner)

    # check result
    assert result == expected
