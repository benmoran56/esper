#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gc
import pickle
import sys
import time
from matplotlib import pyplot

import esper

print("Not yet functional")
sys.exit()

##########################
# Simple timing decorator:
##########################
def timing(f):
    def wrap(*args):
        time1 = time.time()
        ret = f(*args)
        time2 = time.time()
        result_times.append((time2 - time1)*1000.0)
        return ret
    return wrap

##########################
# Create a World instance:
##########################
world = esper.CachedWorld()


#################################
# Define some generic components:
#################################
class Velocity:
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y


class Position:
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y


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


##########################
#  Define some Processors:
##########################
class MovementProcessor(esper.Processor):
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
def create_entities(number):
    for _ in range(number // 2):
        enemy = world.create_entity()
        world.add_component(enemy, Position())
        world.add_component(enemy, Velocity())
        world.add_component(enemy, Health())
        world.add_component(enemy, Command())

        thing = world.create_entity()
        world.add_component(thing, Position())
        world.add_component(thing, Health())
        world.add_component(thing, Damageable())


#################################################
# Perform several queries, and print the results:
#################################################
results = {1: {}, 2: {}, 3: {}}
result_times = []


@timing
def query_entities():
    for _, (_, _) in world.get_components(Position, Velocity):
        pass

create_entities(2000)
for amount in range(1, 5000):
    query_entities()
    print("Query one component, {}".format(amount))

"""
pyplot.ylabel("Time (ms)")
pyplot.xlabel("# Entities")
pyplot.legend(handles=result_times, bbox_to_anchor=(0.5, 1))

pyplot.show()
"""
