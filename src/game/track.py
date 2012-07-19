
""" This is about track """

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

target_a = target_b = map_size = (0, 0)
lap_num = 2
start_pos = (0, 0)
track_num = [1]

class Bar(serge.actor.Actor):
    def __init__(self, name, pos):
        super(Bar, self).__init__('bar', name)
        self.x, self.y = pos
    def addedToWorld(self, world):
        self.setLayerName('main')
    #
    # TODO when recieve game over event
    # destroy itself

def addTrack(world):
    global target_a, target_b, start_pos, map_size, lap_num, track_num
    f = open('track/'+str(track_num[0])+'-track-1')
    #
    # total laps
    line = f.readline()
    lap_num = int(line)
    #
    # the map size
    line = f.readline()
    map_size = map(int, line.split(','))
    #
    # the start line
    line = f.readline()
    points = line.split()
    target_a = _center(map(int, points[0].split(',')), map_size)
    target_b = _center(map(int, points[1].split(',')), map_size)
    #
    # the start pos
    line = f.readline()
    start_pos = _center(map(int, line.split(',')), map_size)
    #
    # read the track
    for twice in range(2):
        line = f.readline()
        points = line.split()
        dx = dy = 0
        for i in range(len(points)):
            points[i] = map(float, points[i].split(','))
            points[i] = _center(map(int, points[i]), map_size)
        p_a = p_b = (0, 0)
        for i in range(len(points)):
            p_a = points[i]
            p_b = points[i - 1]
            serge.blocks.utils.addActorToWorld(
                world,
                Bar('bar'+str(p_a[0])+','+str(p_a[1]), p_a),
                physics = serge.physical.PhysicalConditions(
                    fixed = True,
                    radius = 1,
                    a = (0, 0),
                    b = (p_b[0] - p_a[0], p_b[1] - p_a[1]),
                    friction = 0.4,
                    elasticity = 0,
                    ),
                origin = p_a,
                center_position = p_a,
                )
    f.close()

def _center(p, size):
    p = (p[0] - size[0] / 2, p[1] - size[1] / 2)
    return p
