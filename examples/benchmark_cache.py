#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import time
import optparse

from dataclasses import dataclass as component

from esper import Processor, World

try:
    from matplotlib import pyplot
except ImportError:
    print("The matplotlib module is required for this benchmark.")
    raise Exception

######################
# Commandline options:
######################
parser = optparse.OptionParser()
parser.add_option("-e", "--entities", dest="entities", action="store", default=5000, type="int",
                  help="Change the maximum number of Entities to benchmark. Default is 5000.")

(options, arguments) = parser.parse_args()

MAX_ENTITIES = options.entities
if MAX_ENTITIES <= 50:
    print("The number of entities must be greater than 500.")
    sys.exit(1)


##########################
# Simple timing decorator:
##########################
def timing(f):
    def wrap(*args):
        time1 = time.process_time()
        ret = f(*args)
        time2 = time.process_time()
        current_run.append((time2 - time1) * 1000.0)
        return ret
    return wrap


##########################
# Create a World instance:
##########################
world = World()


#################################
# Define some generic components:
#################################
@component
class Velocity:
    x: float = 0.0
    y: float = 0.0


@component
class Position:
    x: float = 0.0
    y: float = 0.0


@component
class Health:
    hp: int = 100


@component
class Command:
    attack: bool = False
    defend: bool = True


@component
class Projectile:
    size: int = 10
    lifespan: int = 100


@component
class Damageable:
    defense: int = 45


@component
class Brain:
    smarts: int = 9000


##########################
#  Define some Processors:
##########################
class MovementProcessor(Processor):
    def __init__(self):
        super().__init__()

    def process(self):
        for ent, (vel, pos) in self.world.get_components(Velocity, Position):
            pos.x += vel.x
            pos.y += vel.y
            print("Current Position: {}".format((int(pos.x), int(pos.y))))


#############################
# Set up some dummy entities:
#############################
def create_entities(world, number):
    for _ in range(number // 2):
        world.create_entity(Position(), Velocity(), Health(), Command())
        world.create_entity(Position(), Health(), Damageable())


#################################################
# Perform several queries, and print the results:
#################################################
current_run = []
results = []
print("\nFor the first half of each pass, Entities are static.")
print("For the second half, Entities are created/deleted each frame.\n")


@timing
def query_entities(world):
    for _, (_, _) in world.get_components(Position, Velocity):
        pass
    for _, (_, _, _) in world.get_components(Health, Damageable, Position):
        pass


for current_pass in range(10):
    world.clear_database()
    create_entities(world, MAX_ENTITIES)

    print(f"Pass {current_pass + 1}...")

    for amount in range(1, 500):
        query_entities(world)

        if amount > 250:
            world.delete_entity(amount, immediate=True)
            create_entities(world, 1)

    results.append(current_run)
    current_run = []

averaged_results = [sorted(e)[0] for e in zip(*results)]

pyplot.ylabel("Query time (ms)")
pyplot.xlabel("Query of {} entities".format(MAX_ENTITIES))
pyplot.plot(averaged_results, label="Average query time")
pyplot.legend(bbox_to_anchor=(0.5, 1))
pyplot.show()
