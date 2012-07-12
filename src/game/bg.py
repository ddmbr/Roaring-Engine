
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
        self.moveTo(0, 0)

class Ground(serge.blocks.actors.ScreenActor):
    def addedToWorld(self, world):
        super(Ground, self).addedToWorld(world)
        ground_sd = serge.visual.SurfaceDrawing(8000, 6400)
        self.setVisual(ground_sd)
        self.setLayerName('ground')
        #self.moveTo(-4000, -3200)
        self.moveTo(0, 0)
        self.alwaysVisible = True
