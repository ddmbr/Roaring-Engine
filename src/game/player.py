
""" This is a template for an actor """

import pygame
import random

import serge.actor
import serge.visual
import serge.blocks.behaviours

from theme import G

class Player(serge.blocks.actors.ScreenActor):
    def addedToWorld(self, world):
        super(PlayerCar, self).addedToWorld(world)
        #
        # Place the player properly
        self.moveTo(G('player-x'), G('player-y'))
        # TODO set a particular color
        self.setSpriteName('player')
        self.setLayerName('main')
        #
        # Assign behaviour
        self.speed = G('player-speed')
        self.manager = world.findActorByName('behaviours')
        self.control = self.manager.assignBehaviour(
            self,
            serge.blocks.behaviours.KeyboardNSEW(
                self.speed,
                n=pygame.K_k,
                s=pygame.K_j,
                e=pygame.K_l,
                w=pygame.K_h
                ),
            'movement'
            )
        self.keyboard = serge.engine.CurrentEngine().getKeyboard()
    def updateActor(self, interval, world):
        pass
