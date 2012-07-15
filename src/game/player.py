
""" This is class for a player(car) """

import pygame
import random
import math
import socket
import json

import serge.actor
import serge.common
import serge.visual
import serge.blocks.behaviours

from theme import G

import olctlhub

class Player(serge.blocks.actors.ScreenActor):
    def __init__(self, isOLPlay = False, isMainPlayer = True, sock = None, name = ''):
        # TODO modify to enable online playing
        self.isOLPlay = isOLPlay
        self.isMainPlayer = isMainPlayer
        if self.isOLPlay:
            self.sock = sock
        if isMainPlayer:
            super(Player, self).__init__('player', 'player')
        else:
            super(Player, self).__init__('player', name)
    def addedToWorld(self, world):
        """ Add the car to the track and do part of init stuff """
        super(Player, self).addedToWorld(world)
        # TODO set a particular color
        self.setSpriteName('default-car')
        self.setLayerName('main')
        #
        # Assign behaviour
        self.speed = G('player-speed')
        self.manager = world.findActorByName('behaviours')
        if self.isMainPlayer:
            #self.keyboard = serge.engine.CurrentEngine().getKeyboard()
            self.manager.assignBehaviour(
                self,
                KeyControl(),
                'player-movement'
                )
        #
        # Assign physical attributes
        self.force = 3250
        pc = self.physical_conditions
        pc.mass = 900
        pc.width = 48
        pc.height = 64
        pc.friction = 0.2
        #
        # keys constants
        self.GO = 0
        self.BRAKE = 1
        self.LEFT = 2
        self.RIGHT = 3
        self.HANDBRAKE = 4
        self.keys = [0, 0, 0, 0, 0]

    def updateActor(self, interval, world):
        """ Update the car's speed and direction """
        #
        # Update forces and aquire speed
        body = self.physical_conditions.body
        body.reset_forces()
        self.speed = math.sqrt(body.velocity[0] ** 2 + body.velocity[1] ** 2)
        #
        # Handle turn left or turn right
        if self.keys[self.LEFT] and self.speed > 20:
            body.angle -= 0.05
            if not self.keys[self.HANDBRAKE]:
                temp_angle = body.angle - math.pi / 2
                body.apply_impulse(
                    (math.cos(temp_angle) * self.force * 0.02,
                     math.sin(temp_angle) * self.force * 0.02))
                self.brake(0.95)
            else:
                # The car slip
                body.angle -= 0.04
        if self.keys[self.RIGHT] and self.speed > 20:
            body.angle += 0.05
            if not self.keys[self.HANDBRAKE]:
                temp_angle = body.angle + math.pi / 2
                body.apply_impulse(
                    (math.cos(temp_angle) * self.force * 0.02,
                     math.sin(temp_angle) * self.force * 0.02))
                self.brake(0.95)
            else:
                # The car slip
                body.angle += 0.04

        #
        # Leave trace on the road
        if self.keys[self.HANDBRAKE] and self.speed > 200 and random.randint(1, 5) != 4:
            self.trace()
        #
        # the car go foward
        force_x = math.cos(body.angle) * self.force
        force_y = math.sin(body.angle) * self.force
        if self.keys[self.GO]:
            body.apply_force((force_x, force_y), (0, 0))
        if self.keys[self.BRAKE] or \
            (self.keys[self.HANDBRAKE] and self.speed < 100):
            self.brake(0.8)
        #
        # handle friction
        if body.velocity != (0, 0):
            self.brake(0.98)
        # TOO DIRTY!
        if self.speed > 600:
            self.brake(0.97)
        #
        # update camera
        # TODO WRAP it and make it more fluent.
        # TODO Rotate the camera according to the direction of the velocity
        if self.isMainPlayer:
            self.adjustCamera()
        #
        # save the last position
        self.last_pos = (self.x, self.y)
        #
        # Update the info to the server side
        if self.isOLPlay and self.isMainPlayer:
            key_data = json.dumps(['keys', self.keys])
            olctlhub.send(key_data)
            # and adjust all info. if lantency to much then reject
            physical_data = json.dumps(['adjust-physical', [self.x, self.y, body.angle, tuple(body.velocity)]])
            olctlhub.send(physical_data)
        if self.isMainPlayer:
            pass
            #self.log.info(self.speed)
        body.angular_velocity *= 0.9

    def brake(self, value):
        """ Slow down the car """
        body = self.physical_conditions.body
        body.velocity[0] *= value
        body.velocity[1] *= value

    def trace(self):
        # TODO make two traces for both wheels
        """ Leave some trace on the road """
        world = serge.engine.CurrentEngine().getWorld('main-screen')
        ground = world.findActorByName('ground')
        ground_surface = ground._visual.getSurface()
        pygame.draw.line(
            ground_surface,
            (0x50, 0x50, 0x50),
            (self.last_pos[0] + G('track-width') / 2,
                self.last_pos[1] + G('track-height') / 2),
            (self.x + G('track-width') / 2,
                self.y + G('track-height') / 2),
            10
            )
        ground._visual.setSurface(ground_surface)

    def adjustCamera(self):
        camera = serge.engine.CurrentEngine().renderer.getCamera()
        dx, dy = self.getRelativeLocationCentered(camera)
        if (dx < 100 and dx > -100 and dy < 100 and dy > -100):
            camera.update(15)
        else:
            while not (dx < 100 and dx > -100 and dy < 100 and dy > -100):
                camera.update(15)
                dx, dy = self.getRelativeLocationCentered(camera)

class KeyControl(serge.blocks.behaviours.Behaviour):
    """ Control the car with keyboard """

    def __call__(self, world, actor, interval):
        """ Control the car with A, S, D, W and the space key"""
        actor.keys[actor.HANDBRAKE] = actor.keyboard.isDown(pygame.K_SPACE)
        actor.keys[actor.LEFT] = actor.keyboard.isDown(pygame.K_a)
        actor.keys[actor.RIGHT] = actor.keyboard.isDown(pygame.K_d)
        actor.keys[actor.BRAKE] = actor.keyboard.isDown(pygame.K_s)
        actor.keys[actor.GO] = actor.keyboard.isDown(pygame.K_w)

