#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gc
import pickle
import sys
import time
try:
    from matplotlib import pyplot
except:
    print("The matplotlib module is currently required for this benchmark.")
    raise Exception

import esper


##########################
# Simple timing decorator:
##########################
def timing(f):
    def wrap(*args):
        time1 = time.time()
        ret = f(*args)
        time2 = time.time()
        current_run.append((time2 - time1) * 1000.0)
        return ret
    return wrap

##########################
# Create a World instance:
##########################
standard_world = esper.World()
cached_world = esper.CachedWorld()


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
def create_entities(world, number):
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
current_run = []
standard_results = []
cached_results = []


@timing
def query_entities(world):
    for _, (_, _) in world.get_components(Position, Velocity):
        pass

create_entities(standard_world, 5000)
create_entities(cached_world, 5000)

for current_pass in range(5):
    print("Standard World pass {}...".format(current_pass + 1))
    for amount in range(1, 500):
        query_entities(standard_world)
        if amount > 250:
            standard_world.delete_entity(amount)
            standard_world.create_entity()
    standard_results.append(current_run)
    current_run = []

for current_pass in range(5):
    print("Cached World pass {}...".format(current_pass + 1))
    for amount in range(1, 500):
        query_entities(cached_world)
        if amount > 250:
            standard_world.delete_entity(amount)
            cached_world.create_entity()
    cached_results.append(current_run)
    current_run = []

standard_averaged_results = [sorted(e)[0] for e in zip(*standard_results)]
cached_averaged_results = [sorted(e)[0] for e in zip(*cached_results)]

pyplot.ylabel("Query time (ms)")
pyplot.xlabel("Query number")
pyplot.ylim(0, 6)
pyplot.plot(standard_averaged_results, label="Standard")
pyplot.plot(cached_averaged_results, label="Cached")
pyplot.legend(bbox_to_anchor=(0.5, 1))
pyplot.show()
