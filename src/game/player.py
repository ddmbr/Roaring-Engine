
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
import track
import common
import timer

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
        self.target_a = track.target_a
        self.target_b = track.target_b

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
            self.control = self.manager.assignBehaviour(
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
        self.BACK = 1
        self.LEFT = 2
        self.RIGHT = 3
        self.HANDBRAKE = 4
        self.keys = [0, 0, 0, 0, 0]
        #
        # init last pos
        self.last_pos = (self.x, self.y)
        #
        # event linking
        self.lap = 0
        self.broadcaster.linkEvent(common.E_WIN_GAME, self.winGame)
        self.broadcaster.linkEvent(common.E_LOSE_GAME, self.loseGame)

    def updateActor(self, interval, world):
        """ Update the car's speed and direction """
        #
        # Update forces and aquire speed
        body = self.physical_conditions.body
        body.reset_forces()
        #
        # Stop spinning
        body.angular_velocity *= 0.8
        self.speed = math.sqrt(body.velocity[0] ** 2 + body.velocity[1] ** 2)
        #
        # Handle turn left or turn right
        if self.keys[self.LEFT] and self.speed > 20:
            #body.angle -= 0.05
            if not self.keys[self.HANDBRAKE]:
                temp_angle = body.angle - math.pi / 2
                body.apply_impulse(
                    (math.cos(temp_angle) * (self.speed * 0.16),
                     math.sin(temp_angle) * (self.speed * 0.16)),
                    (math.cos(body.angle) * 6, math.sin(body.angle) * 6))
                self.brake(0.99)
            else:
                # The car slip
                body.angle -= 0.09
        if self.keys[self.RIGHT] and self.speed > 20:
            #body.angle += 0.05
            if not self.keys[self.HANDBRAKE]:
                temp_angle = body.angle + math.pi / 2
                body.apply_impulse(
                    (math.cos(temp_angle) * (self.speed * 0.16),
                     math.sin(temp_angle) * (self.speed * 0.16)),
                    (math.cos(body.angle) * 6, math.sin(body.angle) * 6))
                self.brake(0.99)
            else:
                # The car slip
                body.angle += 0.09

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
        #
        # the car braked by handbrake
        if (self.keys[self.HANDBRAKE] and self.speed < 150):
            self.brake(0.8)
        #
        # the car go backward
        if self.keys[self.BACK]:
            body.apply_force((-force_x / 2, -force_y / 2), (0, 0))
        #
        # handle friction
        if body.velocity != (0, 0):
            self.brake(0.98)
        if self.speed > 600:
            self.brake(0.995)
        if self.isMainPlayer:
        #
        # update camera
        # TODO WRAP it and make it more fluent.
        # TODO Rotate the camera according to the direction of the velocity
            self.adjustCamera()
        #
        # Check lap
            x1 = self.last_pos[0]
            y1 = self.last_pos[1]
            x2 = self.x
            y2 = self.y
            x3 = self.target_a[0]
            y3 = self.target_a[1]
            x4 = self.target_b[0]
            y4 = self.target_b[1]
            # 1-2 & 1-3, 1-2 & 1-4
            # 3-4 & 3-1  3-4 & 3-2
            if ((x1 - x2) * (y1 - y3) - (x1 - x3) * (y1 - y2)) * ((x1 - x2) * (y1 - y4) - (x1 - x4) * (y1 - y2)) <= 0 and \
               ((x3 - x4) * (y3 - y1) - (x3 - x1) * (y3 - y4)) * ((x3 - x4) * (y3 - y2) - (x3 - x2) * (y3 - y4)) <= 0:
                if y1 - y2 < 0:
                    self.lap -= 1
                else:
                    self.lap += 1
                    if self.lap == track.lap_num:
                        self.broadcaster.processEvent((common.E_WIN_GAME, self))
                    else:
                        world.msgr.displayMsg(str(self.lap + 1)+'/'+str(track.lap_num)+' lap', 2)
        #
        # save the last position
        self.last_pos = (self.x, self.y)
        #
        # Update the info to the server side
        if self.isOLPlay and self.isMainPlayer:
            key_data = ['keys', self.keys]
            olctlhub.send(key_data)
            # and adjust all info. if lantency to much then reject
            physical_data = ['adjust-physical', [self.x, self.y, body.angle, tuple(body.velocity)]]
            olctlhub.send(physical_data)

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
            (self.last_pos[0] + track.map_size[0] / 2,
                self.last_pos[1] + track.map_size[1] / 2),
            (self.x + track.map_size[0] / 2,
                self.y + track.map_size[1] / 2),
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

    def winGame(self, obj, arg):
        self.world.msgr.displayMsg('You win!', 2)
        self.log.info('win the game')
        self.manager.removeBehavioursByName('player-movement')
        self.keys = [0] * 5
        timer.setTimer(common.E_GAME_OVER, 3)
        olctlhub.send(['win'])

    def loseGame(self, obj, arg):
        self.world.msgr.displayMsg('You lose!', 2)
        self.log.info('lose the game')
        self.manager.removeBehavioursByName('player-movement')
        self.keys = [0] * 5
        timer.setTimer(common.E_GAME_OVER, 3)

    def destroy(self, obj, arg):
        self.world.removeActor(self)

class KeyControl(serge.blocks.behaviours.Behaviour):
    """ Control the car with keyboard """

    def __call__(self, world, actor, interval):
        """ Control the car with A, S, D, W and the space key"""
        actor.keys[actor.HANDBRAKE] = actor.keyboard.isDown(pygame.K_SPACE)
        actor.keys[actor.LEFT] = actor.keyboard.isDown(pygame.K_a)
        actor.keys[actor.RIGHT] = actor.keyboard.isDown(pygame.K_d)
        actor.keys[actor.BACK] = actor.keyboard.isDown(pygame.K_s)
        actor.keys[actor.GO] = actor.keyboard.isDown(pygame.K_w)

