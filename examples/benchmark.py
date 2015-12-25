import time
import gc
import esper

###########################################
# Instantiate the entity and system managers:
###########################################
world = esper.World()
result_times = []


def timing(f):
    def wrap(*args):
        time1 = time.time()
        ret = f(*args)
        time2 = time.time()
        result_times.append((time2 - time1)*1000.0)
        return ret
    return wrap


#################################
# Define some generic components:
#################################
class Velocity:
    def __init__(self):
        self.x = 0
        self.y = 0


class Position:
    def __init__(self):
        self.x = 0
        self.y = 0


class Health:
    def __init__(self):
        self.hp = 100


class Command:
    def __init__(self):
        self.attack = False
        self.defend = True


class Projectile:
    def __init__(self):
        self.size = 10
        self.lifespan = 100


class Damageable:
    def __init__(self):
        self.defense = 45


class Brain:
    def __init__(self):
        self.smarts = 9000


############################
# Set up some dummy entities
############################

def create_entities(number):
    for _ in range(number):
        enemy = world.create_entity()
        world.add_component(enemy, Velocity())
        world.add_component(enemy, Health())
        world.add_component(enemy, Command())
        world.add_component(enemy, Brain())
        world.add_component(enemy, Velocity())
        world.add_component(enemy, Projectile())
        world.add_component(enemy, Damageable())


@timing
def single_comp_query():
    for _, _ in world.get_component(Velocity):
        pass


@timing
def two_comp_query():
    for _, (_, _) in world.get_components(Velocity, Health):
        pass


@timing
def three_comp_query():
    for _, (_, _, _) in world.get_components(Velocity, Health, Command):
        pass


@timing
def four_comp_query():
    for _, (_, _, _, _) in world.get_components(Velocity, Health, Command, Brain):
        pass


for amount in range(1000, 5000, 100):
    create_entities(amount)
    for _ in range(10):
        single_comp_query()
    print("Query one component, {} Entities: {:f} ms".format(amount, sorted(result_times)[0]))
    result_times = []
    world._database = {}                          # Hack to reset database.
    gc.collect()

for amount in range(1000, 5000, 100):
    create_entities(amount)
    for _ in range(10):
        two_comp_query()
    print("Query two components, {} Entities: {:f} ms".format(amount, sorted(result_times)[0]))
    result_times = []
    world._database = {}                          # Hack to reset database.
    gc.collect()

for amount in range(1000, 5000, 100):
    create_entities(amount)
    for _ in range(10):
        three_comp_query()
    print("Query three components, {} Entities: {:f} ms".format(amount, sorted(result_times)[0]))
    result_times = []
    world._database = {}                          # Hack to reset database.
    gc.collect()

for amount in range(1000, 5000, 100):
    create_entities(amount)
    for _ in range(10):
        four_comp_query()
    print("Query four components, {} Entities: {:f} ms".format(amount, sorted(result_times)[0]))
    result_times = []
    world._database = {}                          # Hack to reset database.
    gc.collect()

