
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
        self.force = 500
        self.hand_brake = False
        pc = self.physical_conditions
        pc.mass = 1500
        pc.width = 48
        pc.height = 64
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
            body.angle -= 0.04
            if not self.hand_brake:
                temp_angle = body.angle - math.pi / 2
                body.apply_impulse((math.cos(temp_angle) * self.force * 0.02, math.sin(temp_angle) * self.force * 0.02))
                body.velocity[0] *= 0.97
                body.velocity[1] *= 0.97
            else:
                body.angle -= 0.04
        if self.keyboard.isDown(pygame.K_d):
            body.angle += 0.04
            if not self.hand_brake:
                temp_angle = body.angle + math.pi / 2
                body.apply_impulse((math.cos(temp_angle) * self.force * 0.02, math.sin(temp_angle) * self.force * 0.02))
                body.velocity[0] *= 0.97
                body.velocity[1] *= 0.97
            else:
                body.angle += 0.04

        if self.hand_brake and self.speed > 200 and random.randint(1, 5) != 4:
            world = serge.engine.CurrentEngine().getWorld('main-screen')
            ground = world.findActorByName('ground')
            ground_surface = ground._visual.getSurface()
            pygame.draw.line(
                ground_surface,
                (0x50, 0x50, 0x50),
                (self.last_pos[0] + G('track-width') / 2, self.last_pos[1] + G('track-height') / 2),
                (self.x + G('track-width') / 2, self.y + G('track-height') / 2),
                10
                )
            #pygame.draw.circle(
            #    ground_surface,
            #    (0x50, 0x50, 0x50),
            #    (int(self.x) + 4000, int(self.y) + 3200),
            #    10
            #    )
            ground._visual.setSurface(ground_surface)

        force_x = math.cos(body.angle) * self.force
        force_y = math.sin(body.angle) * self.force
        if self.keyboard.isDown(pygame.K_w):
            body.apply_force((force_x, force_y), (0, 0))
        if self.keyboard.isDown(pygame.K_s) or (self.hand_brake and self.speed < 200):
            self.brake()
        #
        # handle friction
        if body.velocity != (0, 0):
            body.velocity[0] *= 0.97
            body.velocity[1] *= 0.97
        # 0-200-600-800, 0-200-440-640
        camera = serge.engine.CurrentEngine().renderer.getCamera()
        dx, dy = self.getRelativeLocationCentered(camera)
        if dx < 100 and dx > -100 and dy < 100 and dy > -100:
            camera.update(10)
        else:
            while not (dx < 100 and dx > -100 and dy < 100 and dy > -100):
                camera.update(10)
                dx, dy = self.getRelativeLocationCentered(camera)
        if self.keyboard.isDown(pygame.K_o):
            camera.zoom *= 0.9
        #
        # save the last position
        self.last_pos = (self.x, self.y)
        #print (-body.velocity[0] ** 2 * 0.02, -body.velocity[1] ** 2 * 0.02), body.velocity
        self.log.info(int(self.speed))
    def brake(self):
        body = self.physical_conditions.body
        body.velocity[0] *= 0.8
        body.velocity[1] *= 0.8
