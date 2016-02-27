from scene import *
import esper

##################################
## Here are a couple of Components
##################################      
class Renderable(SpriteNode):
    def __init__(self, **kwargs):
        SpriteNode.__init__(self, **kwargs)
 
      
class Velocity:
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y


##############
## A processor
##############                     
class MovementProcessor(esper.Processor):
    def __init__(self):
        super().__init__()
        
    def process(self):
        for ent, (rend, vel) in self.world.get_components(Renderable, Velocity):
            rend.position += (vel.x, vel.y)
            move_action = Action.move_to(rend.position[0], rend.position[1], 0.7)
            rend.run_action(move_action)


class MyScene (Scene):
    def setup(self):
        #Create a World Object
        self.newworld = esper.World()
        
        #Add the processor
        self.movement_processor = MovementProcessor()
        self.newworld.add_processor(self.movement_processor)
        
        #Create a couple of entities
        self.player = self.newworld.create_entity()
        self.newworld.add_component(self.player, Renderable(parent=self,
                               texture='plc:Character_Boy', position=(100, 100)))
        self.newworld.add_component(self.player, Velocity(x=1, y=.5))
        
        self.enemy = self.newworld.create_entity()
        self.newworld.add_component(self.enemy, Renderable(parent=self,
                               texture='plc:Character_Pink_Girl', position=(200, 200)))
        self.newworld.add_component(self.enemy, Velocity(x=.5, y=0))
    
    def did_change_size(self):
        pass
    
    def update(self):
        # Process the world at each update!
        self.newworld.process()
    
    def touch_began(self, touch):
        pass
    
    def touch_moved(self, touch):
        pass
    
    def touch_ended(self, touch):
        pass

if __name__ == '__main__':
    run(MyScene(), show_fps=True)