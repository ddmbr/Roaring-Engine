
""" This is a template for an actor """

import pygame
import random
import math

import serge.actor
import serge.common
import serge.visual
import serge.blocks.behaviours

from theme import G

class Background(serge.blocks.actors.ScreenActor):
    def addedToWorld(self, world):
        super(Background, self).addedToWorld(world)
        # TODO place-holder
        self.setSpriteName('default-background')
        self.setLayerName('background')
