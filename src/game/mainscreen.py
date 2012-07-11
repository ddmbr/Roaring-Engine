import random
import pygame

import serge.actor
import serge.visual
import serge.events
import serge.common
import serge.blocks.utils
import serge.blocks.behaviours
import serge.blocks.actors

from theme import G

class MainScreen(serge.blocks.actors.ScreenActor):
    """The logic for the main screen"""
    def __init__(self):
        super(MainScreen, self).__init__('item', 'main-screen')
    def addedToWorld(self, world):
        super(MainScreen, self).addedToWorld(world)
        self.manager = world.findActorByName('behaviours')
        #
        #Now add actors to the world
        #
        #for example,
        #
        #   self.player = serge.blocks.utils.addActorToWorld(
        #       world,
        #       player.PlayerCar('player', 'player')
        #       )
        #

def main():
    world = serge.engine.CurrentEngine().getWorld('main-screen')
    manager = serge.blocks.behaviours.BehaviourManager('behaviours', 'behaviours')
    world.addActor(manager)
    s = MainScreen()
    world.addActor(s)
