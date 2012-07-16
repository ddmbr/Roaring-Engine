
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
        self.setSpriteName('1-track')
        self.setLayerName('background')
        self.moveTo(0, 0)

class Ground(serge.blocks.actors.ScreenActor):
    def addedToWorld(self, world):
        super(Ground, self).addedToWorld(world)
        ground_sd = serge.visual.SurfaceDrawing(G('track-width'), G('track-height'))
        self.setVisual(ground_sd)
        self.setLayerName('ground')
        self.moveTo(0, 0)
        self.alwaysVisible = True
