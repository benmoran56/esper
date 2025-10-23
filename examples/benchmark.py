#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gc
import random
import sys
import time
import optparse

from dataclasses import dataclass as component

import esper

######################
# Commandline options:
######################
parser = optparse.OptionParser()
parser.add_option("-p", "--plot", dest="plot", action="store_true", default=False,
                  help="Display benchmark. Requires matplotlib module.")
parser.add_option("-w", "--walltime", dest="walltime", action="store_true", default=False,
                  help="Benchmark the 'wall clock' time, instead of process time.")
parser.add_option("-e", "--entities", dest="entities", action="store", default=5000, type="int",
                  help="Change the maximum number of Entities to benchmark. Default is 5000.")

(options, arguments) = parser.parse_args()

MAX_ENTITIES = options.entities
if MAX_ENTITIES <= 500:
    print("The number of entities must be greater than 500.")
    sys.exit(1)

if options.walltime:
    print("Benchmarking wall clock time...\n")
    time_query = time.time
else:
    time_query = time.process_time


##########################
# Simple timing decorator:
##########################
def timing(f):
    def wrap(*args):
        time1 = time_query()
        ret = f(*args)
        time2 = time_query()
        result_times.append((time2 - time1)*1000.0)
        return ret
    return wrap


#################################
# Define some generic components:
#################################
@component
class Velocity:
    x: int = 0
    y: int = 0


@component
class Position:
    x: int = 0
    y: int = 0


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


@component
class IsPlayer:
    pass


#############################
# Set up some dummy entities:
#############################
def create_entities(number):
    for _ in range(number // 2):
        esper.create_entity(Position(), Velocity(), Health(), Command())
        esper.create_entity(Position(), Health(), Damageable())


def create_mixed_entities(number):
    for _ in range(number - 5):
        esper.create_entity(Position(), Velocity())

    for _ in range(5):
        esper.create_entity(Position(), Velocity(), IsPlayer())


#############################
# Some timed query functions:
#############################
@timing
def single_comp_query():
    for _, _ in esper.get_component(Position):
        pass


@timing
def two_comp_query():
    for _, (_, _) in esper.get_components(Position, Velocity):
        pass


@timing
def three_comp_query():
    for _, (_, _, _) in esper.get_components(Position, Damageable, Health):
        pass


@timing
def rare_comp_query():
    """
    Benchmark a query involving a common and a rare component.

    This scenario is designed to highlight the performance gain from the
    "iterate over the smallest set" optimization. The query for
    (Position, Velocity, IsPlayer) should be extremely fast, as it only
    needs to iterate over the few entities that have the rare `IsPlayer`
    component, instead of all entities with `Position`.
    """
    for _, (_, _, _) in esper.get_components(Position, Velocity, IsPlayer):
        pass


@timing
def dynamic_world_frame(entities_to_kill, new_entities_to_create):
    """
    Benchmark a single frame in a dynamic world with entity churn.

    This function simulates a typical game loop frame to measure performance
    under dynamic conditions. It tests the combined cost of:
    1. Running common queries.
    2. Deleting a batch of existing entities (testing `delete_entity`).
    3. Creating a batch of new entities (testing `create_entity`).
    4. Cleaning up dead entities (testing `clear_dead_entities`).

    This is a good test for the lazy cache invalidation and optimized
    entity cleanup mechanisms.
    """
    for _, (_, _) in esper.get_components(Position, Velocity):
        pass
    for _, (_, _, _) in esper.get_components(Position, Damageable, Health):
        pass

    for ent_id in entities_to_kill:
        if esper.entity_exists(ent_id):
            esper.delete_entity(ent_id, immediate=False)

    create_entities(new_entities_to_create)

    esper.clear_dead_entities()


#################################################
# Perform several queries, and print the results:
#################################################
results = {1: {}, 2: {}, 3: {}}
# result_times = []
new_results = {"Rare Comp": {}, "Dynamic World": {}}
result_times = []

for amount in range(500, MAX_ENTITIES, MAX_ENTITIES//50):
    create_entities(amount)
    for _ in range(50):
        single_comp_query()

    result_min = min(result_times)
    print("Query one component, {} Entities: {:f} ms".format(amount, result_min))
    results[1][amount] = result_min
    result_times = []
    esper.clear_database()
    gc.collect()

for amount in range(500, MAX_ENTITIES, MAX_ENTITIES//50):
    create_entities(amount)
    for _ in range(50):
        two_comp_query()

    result_min = min(result_times)
    print("Query two components, {} Entities: {:f} ms".format(amount, result_min))
    results[2][amount] = result_min
    result_times = []
    esper.clear_database()
    gc.collect()

for amount in range(500, MAX_ENTITIES, MAX_ENTITIES//50):
    create_entities(amount)
    for _ in range(50):
        three_comp_query()

    result_min = min(result_times)
    print("Query three components, {} Entities: {:f} ms".format(amount, result_min))
    results[3][amount] = result_min
    result_times = []
    esper.clear_database()
    gc.collect()


print("\n--- Benchmarking: Optimized Scenarios ---")

for amount in range(500, MAX_ENTITIES, MAX_ENTITIES//50):
    create_mixed_entities(amount)
    for _ in range(50):
        rare_comp_query()
    result_min = min(result_times)
    print("Query rare component, {} Entities: {:f} ms".format(amount, result_min))
    new_results["Rare Comp"][amount] = result_min
    result_times = []
    esper.clear_database()
    gc.collect()

for amount in range(500, MAX_ENTITIES, MAX_ENTITIES//50):
    create_entities(amount)
    all_entities = list(esper._entities.keys())
    k = min(10, len(all_entities))
    entities_to_kill_per_frame = random.sample(all_entities, k=k)

    for _ in range(50):
        dynamic_world_frame(entities_to_kill_per_frame, 10)
        all_entities = list(esper._entities.keys())
        k = min(10, len(all_entities))
        if k > 0:
            entities_to_kill_per_frame = random.sample(all_entities, k=k)

    result_min = min(result_times)
    print("Dynamic world frame, {} Entities: {:f} ms".format(amount, result_min))
    new_results["Dynamic World"][amount] = result_min
    result_times = []
    esper.clear_database()
    gc.collect()


#############################################
# Save the results to disk, or plot directly:
#############################################

if not options.plot:
    print("\nRun 'benchmark.py --help' for details on plotting this benchmark.")

if options.plot:
    try:
        from matplotlib import pyplot as plt
    except ImportError:
        print("\nThe matplotlib module is required for plotting results.")
        sys.exit(1)

    plt.figure(1)
    lines = []
    for num, result in results.items():
        x, y = zip(*sorted(result.items()))
        label = '%i Component%s' % (num, '' if num == 1 else 's')
        lines.extend(plt.plot(x, y, label=label))

    plt.ylabel("Query Time (ms)")
    plt.xlabel("Number of Entities")
    plt.title("Basic Component Queries")
    plt.legend(handles=lines, bbox_to_anchor=(0.5, 1))

    plt.figure(2)
    lines = []
    for name, result in new_results.items():
        if result:
            x, y = zip(*sorted(result.items()))
            lines.extend(plt.plot(x, y, label=name, marker='o'))

    plt.ylabel("Query Time (ms)")
    plt.xlabel("Number of Entities")
    plt.title("Optimized Scenarios")
    plt.legend(handles=lines, bbox_to_anchor=(0.5, 1))

    plt.show()
