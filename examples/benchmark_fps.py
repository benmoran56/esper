"""
This benchmark is designed to test how many entities a world can process in the
span of one second (frames per second). This metric is used to determine at what
point that Esper is no longer able to process all entities each frame (takes
longer than one frames time to process).

Configuration: You can adjust NUM_ENTITIES to be whatever number you want to see
how fast Esper is on your system. If you are on a fast computer and Esper is
processing faster than TARGET_FPS, you can set WHITTLE to True, which will tell
the benchmark to try to add more entities until fps == TARGET_FPS.
"""

import math, time, esper

CTM = lambda: round(time.time() * 1000)

class Life:
    def __init__(self):
        self.cur_hp = 100
        self.max_hp = 100

    def breathe(self):
        pass

class Breathe(esper.Processor):
    def process(self):
        for ent, (life,) in self.world.get_components(Life):
            life.breathe()

world = esper.World()
world.add_processor(Breathe())

TARGET_FPS = 60
NUM_ENTITIES = 25700#19900
entities = []
for i in range(NUM_ENTITIES):
    entities.append(world.create_entity(Life()))

avg = []
WHITTLE = False  # Choose whether to try to get down to target fps during test
RUN_CONTINUOUSLY = False
try:
    for _ in range(60):  # One minute
        fps = 0
        start = CTM()
        while CTM() < start + 1000:
            world.process()
            fps += 1
        print('FPS with', len(entities), 'entities:', fps)
        avg.append((fps, len(entities)))

        # WHITTLE down FPS gradually to reach target fps
        if WHITTLE:
            if fps > TARGET_FPS:
                for i in range(100):#math.ceil(fps / TARGET_FPS) - 1 + TARGET_FPS):
                    entities.append(world.create_entity(Life()))
    if not RUN_CONTINUOUSLY:
        raise KeyboardInterrupt()
except KeyboardInterrupt:
    avg_fps = [fps for (fps, _) in avg]
    avg_fps = sum(avg_fps) / len(avg_fps)
    avg_ent = [ent for (_, ent) in avg]
    avg_ent = sum(avg_ent) / len(avg_ent)
    print('Had an average FPS of', avg_fps, 'with an average of', avg_ent, 'entities')
