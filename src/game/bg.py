
""" This is a template for an actor """

import pygame
import random
import math

import serge.actor
import serge.common
import serge.visual
import serge.blocks.behaviours

from theme import G
import track

class Background(serge.blocks.actors.ScreenActor):
    def __init__(self):
        super(Background, self).__init__('bg', 'bg')
        self.track_num = track.track_num[0]
    def addedToWorld(self, world):
        super(Background, self).addedToWorld(world)
        # TODO place-holder
        self.setSpriteName(str(self.track_num)+'-track')
        self.setLayerName('background')
        self.moveTo(0, 0)

class Ground(serge.blocks.actors.ScreenActor):
    def addedToWorld(self, world):
        super(Ground, self).addedToWorld(world)
        ground_sd = serge.visual.SurfaceDrawing(*track.map_size)
        self.setVisual(ground_sd)
        self.setLayerName('ground')
        self.moveTo(0, 0)
        self.alwaysVisible = True
