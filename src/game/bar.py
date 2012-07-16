
""" This is class for a bar(fence) """

import pygame
import random
import math
import socket
import json

import serge.actor
import serge.common
import serge.visual
import serge.blocks.behaviours
import serge.blocks.actors
import serge.blocks.utils

from theme import G

import olctlhub

class Bar(serge.actor.Actor):
    def __init__(self, name, pos):
        super(Bar, self).__init__('bar', name)
        print pos
        self.x, self.y = pos
    def addedToWorld(self, world):
        #self.setSpriteName('default-car')
        self.setLayerName('main')

def addTrack(world):
    f = open('track/1-track-1')
    line = f.readline()
    while line != '':
        points = line.split()
        dx = dy = 0
        for i in range(len(points)):
            points[i] = map(float, points[i].split(','))
            points[i] = map(int, points[i])
        print points
        p_a = p_b = (0, 0)
        for i in range(len(points)):
            p_a = (points[i][0] - G('track-width') / 2, points[i][1] - G('track-height') / 2)
            p_b = (points[i - 1][0] - G('track-width') / 2, points[i - 1][1] - G('track-height') / 2)
            serge.blocks.utils.addActorToWorld(
                world,
                Bar('bar'+str(p_a[0])+','+str(p_a[1]), p_a),
                physics = serge.physical.PhysicalConditions(
                    fixed = True,
                    radius = 1,
                    a = (0, 0),
                    b = (p_b[0] - p_a[0], p_b[1] - p_a[1]),
                    friction = 0.2,
                    elasticity = 0.3,
                    ),
                origin = p_a,
                center_position = p_a,
                )
        line = f.readline()
    f.close()
