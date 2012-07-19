import time

import serge.actor
import serge.engine

class Timer(serge.blocks.actors.ScreenActor):
    def __init__(self, event, timeout):
        super(Timer, self).__init__('timer', 'timer')
        self.event = event
        self.timeout = timeout
        self.startTime = time.time()
    def updateActor(self, interval, world):
        if time.time() >= self.startTime + self.timeout:
            self.broadcaster.processEvent((self.event, self))
            world.removeActor(self)

def setTimer(event, timeout):
    world = serge.engine.CurrentEngine().getCurrentWorld()
    world.addActor(Timer(event, timeout))
    
