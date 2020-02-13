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
NUM_ENTITIES = 19900
entities = []
for i in range(NUM_ENTITIES):
    entities.append(world.create_entity(Life()))

avg = []
try:
    while True:
        fps = 0
        start = CTM()
        while CTM() < start + 1000:
            world.process()
            fps += 1
        print(f'FPS with {len(entities)} entities:', fps)
        avg.append((fps, len(entities)))
        # if fps > TARGET_FPS:
        #     for i in range(3):#math.ceil(fps / TARGET_FPS) - 1 + TARGET_FPS):
        #         entities.append(world.create_entity(Life()))
except KeyboardInterrupt:
    avg_fps = [fps for (fps, _) in avg]
    avg_fps = sum(avg_fps) / len(avg_fps)
    avg_ent = [ent for (_, ent) in avg]
    avg_ent = sum(avg_ent) / len(avg_ent)
    print(f'Had an average FPS of {avg_fps} with an average of {avg_ent} entities')
