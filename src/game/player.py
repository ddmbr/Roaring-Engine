
""" This is a template for an actor """

import pygame
import random
import math

import serge.actor
import serge.common
import serge.visual
import serge.blocks.behaviours

from theme import G

class Player(serge.blocks.actors.ScreenActor):
    def addedToWorld(self, world):
        super(Player, self).addedToWorld(world)
        # TODO set a particular color
        self.setSpriteName('default-car')
        self.setLayerName('main')
        #
        # Assign behaviour
        self.speed = G('player-speed')
        self.manager = world.findActorByName('behaviours')
        self.keyboard = serge.engine.CurrentEngine().getKeyboard()
        #
        # Assign physics
        self.force = 400
        self.hand_brake = False
        pc = self.physical_conditions
        pc.mass = 1500
        pc.width = 64
        pc.height = 80
        pc.friction = 10
        #self.setPhysical(self.physical_conditions)
        #
        # Place the player properly
        self.moveTo(G('player-x'), G('player-y'))

    def updateActor(self, interval, world):
        body = self.physical_conditions.body
        body.reset_forces()
        self.speed = math.sqrt(body.velocity[0] ** 2 + body.velocity[1] ** 2)
        if self.keyboard.isDown(pygame.K_SPACE):
            self.hand_brake = True
        else:
            self.hand_brake = False
        if self.keyboard.isDown(pygame.K_a):
            body.angle -= 0.02
            if not self.hand_brake:
                body.velocity[0] = self.speed * math.cos(body.angle)
            else:
                body.angle -= 0.02
                print "DRIFT"
        if self.keyboard.isDown(pygame.K_d):
            body.angle += 0.02
            if not self.hand_brake:
                body.velocity[1] = self.speed * math.sin(body.angle)
            else:
                body.angle += 0.02
                print "DRIFT"
        force_x = math.cos(body.angle) * self.force
        force_y = math.sin(body.angle) * self.force
        if self.keyboard.isDown(pygame.K_w):
            body.apply_force((force_x, force_y), (0, 0))
        if self.keyboard.isDown(pygame.K_s):
            body.apply_force((-force_x / 2, -force_y / 2), (0, 0))
        if body.velocity != (0, 0):
            body.velocity[0] *= 0.96
            body.velocity[1] *= 0.96
        #0-200-600-800, 0-200-440-640
        camera = serge.engine.CurrentEngine().renderer.getCamera()
        dx, dy = self.getRelativeLocationCentered(camera)
        if dx < 100 and dx > -100 and dy < 100 and dy > -100:
            camera.update(10)
        else:
            while not (dx < 100 and dx > -100 and dy < 100 and dy > -100):
                camera.update(10)
                dx, dy = self.getRelativeLocationCentered(camera)
        # save the last position
        self.last_pos = (self.x, self.y)
        #print (-body.velocity[0] ** 2 * 0.02, -body.velocity[1] ** 2 * 0.02), body.velocity
