"""Classes the implement behaviours"""

import pygame
import os

import serge.actor
import serge.engine
import serge.common
import serge.events

class MissingBehaviour(Exception): """Could not locate the behaviour"""
class DuplicateBehaviour(Exception): """The behaviour was already recorded"""
class BehaviourNotPaused(Exception): """The behaviour was not paused"""
class BehaviourAlreadyPaused(Exception): """The behaviour was already paused"""

B_FINISHED = 'finished' # A behaviour has run and can now be paused
B_COMPLETED = 'completed' # A behaviour can be removed

### Main classes for implementing behaviours ###


class BehaviourRecord(object):
    """Represents a record of a requested behaviour"""
    
    def __init__(self, actor, behaviour, name):
        """Initialise the record"""
        self._actor = actor
        self._behaviour = behaviour
        self._name = name
        self._running = True
        self._complete = False
        if isinstance(behaviour, Behaviour):
            self._behaviour.record = self
                
    def performBehaviour(self, interval, world):
        """Perform the actual behaviour"""
        if self._running:
            result = self._behaviour(world, self._actor, interval)
            if result in (B_FINISHED, B_COMPLETED):
                self.pause()
                if result == B_COMPLETED:
                    self.markComplete()
        
    def pause(self):
        """Pause the behaviour"""
        if self._running:
            self._running = False
        else:
            raise BehaviourAlreadyPaused('The behaviour %s was not paused' % self)

    def restart(self):
        """Restart the behaviour"""
        if not self._running:
            self._running = True
        else:
            raise BehaviourNotPaused('The behaviour %s was already running' % self)

    def matches(self, actor, name):
        """Return True if this behaviour matches the actor and name"""
        return self._actor == actor and self._name == name

    def matchesName(self, name):
        """Return True if this behaviour matches the name"""
        return self._name == name

    def _getId(self):
        """Return an id to identify the behaviour"""
        nice_name = 'the game' if self._actor is None else self._actor.getNiceName()
        return '%s-%s' % (self._name, nice_name)
        
    def isRunning(self):
        """Return True if we are running"""
        return self._running
    
    def markComplete(self):
        """Mark the behaviour as complete
        
        The manage can now remove us and no longer try calling.
        
        """
        self._complete = True
        
    def isComplete(self):
        """Return True if we are complete"""
        return self._complete
                     
    def involvesActor(self, actor):
        """Return True if the behaviour involves the actor"""
        return self._actor is actor
                         
                         
class BehaviourManager(serge.actor.Actor):
    """Manages the behaviour of multiple actors in a world"""
    
    def __init__(self, *args, **kw):
        """Initialise the manager"""
        super(BehaviourManager, self).__init__(*args, **kw)
        self._behaviours = {}
        
    def assignBehaviour(self, actor, behaviour, name):
        """Assign a behaviour to an actor"""
        record = BehaviourRecord(actor, behaviour, name)
        if record._getId() in self._behaviours:
            raise DuplicateBehaviour('The behaviour %s,%s was already recorded' % (actor, behaviour))
        nice_name = 'the game' if actor is None else actor.getNiceName()
        self.log.info('Assigned behaviour %s to %s' % (behaviour, nice_name))
        self._behaviours[record._getId()] = record
        if actor:
            actor.linkEvent(serge.events.E_REMOVED_FROM_WORLD, self._actorRemoved)
        return record
        
    def removeBehaviour(self, record):
        """Remove a particular behaviour"""
        try:
            del(self._behaviours[record._getId()])
        except KeyError:
            raise MissingBehaviour('The behaviour %s was not found' % record)

    def removeBehaviours(self, behaviours):
        """Remove a list of behaviours"""
        for behaviour in behaviours:
            self.removeBehaviour(behaviour)
            
    def hasBehaviour(self, record):
        """Return True if we have a particular behaviour record"""
        return record in self._behaviours.values()

    def removeBehaviourByName(self, actor, name):
        """Remove the named behaviour for an actor based on its name"""
        for record in self._behaviours.values():
            if record.matches(actor, name):
                self.removeBehaviour(record)
                return
        raise MissingBehaviour('Not behaviour named "%s" found for actor "%s"' % (name, actor.getNiceName()))

    def removeBehavioursByName(self, name):
        """Remove the named behaviour for all actors based on a name"""
        for record in self._behaviours.values():
            if record.matchesName(name):
                self.removeBehaviour(record)

    def updateActor(self, world, interval):
        """Perform all our behaviours"""
        completed = []
        #
        # Perform all the behaviours
        for behaviour in self._behaviours.values():
            behaviour.performBehaviour(world, interval)
            if behaviour.isComplete():
                completed.append(behaviour)
        #
        self.removeBehaviours(completed)
        
    def pauseBehaviours(self, name):
        """Pause all behaviours with the name"""
        for record in self._behaviours.values():
            if record.matchesName(name):
                record.pause()

    def restartBehaviours(self, name):
        """Restart all behaviours with the name"""
        for record in self._behaviours.values():
            if record.matchesName(name):
                record.restart()
        
    def _actorRemoved(self, actor, arg):
        """An actor was removed from the world
        
        We should remove any behaviours linked to this actor.
        
        """
        to_remove = []
        for behaviour in self._behaviours.values():
            if behaviour.involvesActor(actor):
                to_remove.append(behaviour)
        #
        self.removeBehaviours(to_remove)
        
class Behaviour(serge.common.Loggable):
    """Base class for all behaviours"""
    
    def __init__(self):
        """Initialise the behaviour"""
        self.addLogger()
        self.active = True
        
    def __call__(self, world, actor, interval):
        """Execute the behaviour"""
        raise NotImplementedError
            
            
### Some useful behaviours ###

class SnapshotOnKey(Behaviour):
    """Take a snapshot of the screen when the user presses a key"""

    def __init__(self, key=pygame.K_s, size=(800, 600), location='', overwrite=True):
        """Initialise the ScreenShotOnKey"""
        super(SnapshotOnKey, self).__init__()
        self.key = key
        self.size = size
        self.location = location
        self.overwrite = overwrite
        self.engine = serge.engine.CurrentEngine()
        self.keyboard = self.engine.getKeyboard()
        self.snapshots = 1
                
    def __call__(self, world, actor, interval):
        """Check for screenshots"""
        if self.keyboard.isClicked(self.key):
            surface = self.engine.getRenderer().getSurface()
            rect = self.size
            #
            # Find the filename
            while True:
                filename = os.path.join(self.location, 'screenshot-%d.png' % self.snapshots)
                if self.overwrite or not os.path.exists(filename):
                    break
                self.snapshots += 1
            #
            # Save file
            self.log.info('Taking snapshot %d' % self.snapshots)
            try:
                pygame.image.save(surface.subsurface(rect), filename)
            except Exception, err:
                self.log.error('Unable to save snapshot "%s": %s' % (filename, err))
            self.snapshots += 1



class MoveTowardsPoint(Behaviour):
    """Move an actor towards a point"""
    
    def __init__(self, point, x_speed=1, y_speed=1):
        """Initialise the behaviour
        
        You can limit the directions that will be moved by setting
        x_speed or y_speed to be 0.
        
        """
        super(MoveTowardsPoint, self).__init__()
        self._target = point
        self._x_speed = x_speed
        self._y_speed = y_speed
        
    def __call__(self, world, actor, interval):
        """Do the movement"""
        dx = (self._target[0] - actor.x)
        if dx > 0:
            actor.x += min(dx, self._x_speed)
        elif dx < 0:
            actor.x -= min(abs(dx), self._x_speed)
        #   
        dy = (self._target[1] - actor.y)
        if dy > 0:
            actor.y += min(dy, self._y_speed)
        elif dy < 0:
            actor.y -= min(abs(dy), self._y_speed)


class MoveTowardsActor(Behaviour):
    """Move an actor towards another actor"""
    
    def __init__(self, actor, x_speed=1, y_speed=1):
        """Initialise the behaviour
        
        You can limit the directions that will be moved by setting
        x_speed or y_speed to be 0.
        
        """
        super(MoveTowardsActor, self).__init__()
        self._target = actor
        self._x_speed = x_speed
        self._y_speed = y_speed
        
    def __call__(self, world, actor, interval):
        """Do the movement"""
        dx = (self._target.x - actor.x)
        if dx > 0:
            actor.x += min(dx, self._x_speed)
        elif dx < 0:
            actor.x -= min(abs(dx), self._x_speed)
        #   
        dy = (self._target.y - actor.y)
        if dy > 0:
            actor.y += min(dy, self._y_speed)
        elif dy < 0:
            actor.y -= min(abs(dy), self._y_speed)
     

class MoveWithMouse(Behaviour):
    """Move the actor with the mouse"""

    def __init__(self, actor):
        """Initialise the MoveWithMouse"""
        super(MoveWithMouse, self).__init__()
        self.actor = actor
        self.mouse = serge.engine.CurrentEngine().getMouse()
        
    def __call__(self, world, actor, interval):
        """Move to the mouse position"""
        x, y = self.mouse.getScreenPos()
        self.actor.moveTo(x, y)

        
class AvoidActor(Behaviour):
    """Move away from an actor until you reach a certain distance"""
    
    def __init__(self, actor, x_speed=1, y_speed=1, distance=10):
        """Initialise the behaviour
        
        You can limit the directions that will be moved by setting
        x_speed or y_speed to be 0.
        
        """
        super(AvoidActor, self).__init__()
        self._target = actor
        self._distance = distance
        self._x_speed = x_speed
        self._y_speed = y_speed
        
    def __call__(self, world, actor, interval):
        """Do the movement if we are within range"""
        #
        # Check if we are outside of the given distance
        dx = (self._target.x - actor.x)
        dy = (self._target.y - actor.y)
        if (dx**2 + dy**2) > self._distance**2:
            return
        #
        if dx > 0:
            actor.x -= self._x_speed
        elif dx < 0:
            actor.x += self._x_speed
        #   
        if dy > 0:
            actor.y -= self._y_speed
        elif dy < 0:
            actor.y += self._y_speed


class AvoidActorsWithTag(Behaviour):
    """Move away from multiple actors until you read a certain distance"""

    def __init__(self, tag, x_speed=1, y_speed=1, distance=10):
        """Initialise the behaviour"""
        super(AvoidActorsWithTag, self).__init__()
        self._distance = distance
        self._x_speed = x_speed
        self._y_speed = y_speed
        self._tag = tag

    def __call__(self, world, actor, interval):
        """Do the movement if we are within range"""
        encroachers = []
        for target in world.findActorsByTag(self._tag):
            #
            # Check if we are outside of the given distance
            if target != actor:
                dx = (target.x - actor.x)
                dy = (target.y - actor.y)
                dist = (dx**2 + dy**2)
                if dist < self._distance**2:
                    encroachers.append((dist, dx, dy, target))
        #
        if encroachers:
            encroachers.sort()
            _, dx, dy, _ = encroachers[0]
            #
            if dx > 0:
                actor.x -= self._x_speed
            elif dx < 0:
                actor.x += self._x_speed
            #   
            if dy > 0:
                actor.y -= self._y_speed
            elif dy < 0:
                actor.y += self._y_speed

class FlashFor(Behaviour):
    """Flash an actor on the screen
    
    When the actor is flashing the property flashing is True.
    
    """

    def __init__(self, actor, time):
        """Initialise the FlashFor"""
        actor.flashing = False
        self._initial_time = time
        self._time = time
        self._actor = actor

    def __call__(self, world, actor, interval):
        """Perform the behaviour"""
        self._time -= interval/1000.0
        if self._time <= 0:
            self._actor.flashing = False
            self._actor.visible = True
            self._time = self._initial_time
            return B_FINISHED
        else:
            self._actor.flashing = True
            self._actor.visible = not self._actor.visible
            
class TwoOptions(Behaviour):
    """A behaviour that chooses between two optional behaviours"""
    
    def __init__(self, b1, b2, arg, selector):
        """Initialise the behaviour
        
        b1 and b2 are the two behaviours that we want to choose between.
        The selector function will be called by passing 'arg' to it. The
        selector should return True to activate b1, False for b2.
        
        """
        super(TwoOptions, self).__init__()
        self._b1 = b1
        self._b2 = b2
        self._arg = arg
        self._selector = selector
        
    def __call__(self, world, actor, interval):
        """Do the appropriate behaviour"""
        if self._selector(self._arg):
            self._b1(world, actor, interval)
        else:
            self._b2(world, actor, interval)
            
class Optional(TwoOptions):
    """A behaviour that is turned on and off by an option"""
    
    def __init__(self, behaviour, arg, selector):
        """Initialise the behaviour
        
        The selector function will be called by passing 'arg' to it. The
        selector should return True to activate the behaviour
        
        """
        super(Optional, self).__init__(behaviour, lambda a,b,c:None, arg, selector)         


### Control behaviours ###


class KeyboardNSEW(Behaviour):
    """Move an actor in ordinal directions according to the keyboard
    
    Set the n, s, e and w to the keys you want to move the actor. If you
    do not want any motion then set that direction to None. Set the speed
    to be the amount to move per keypress.
    
    """
    
    def __init__(self, speed, n=pygame.K_UP, s=pygame.K_DOWN, e=pygame.K_RIGHT, w=pygame.K_LEFT):
        """Initialise the behaviour"""
        super(KeyboardNSEW, self).__init__()
        self._speed = speed
        self._n = n
        self._s = s
        self._e = e
        self._w = w
        self._keyboard = serge.engine.CurrentEngine().getKeyboard()
        
    def __call__(self, world, actor, interval):
        """Perform the motion"""
        if actor.active:
            dy = dx = 0
            if self._n and self._keyboard.isDown(self._n):
                dy = -self._speed
            if self._s and self._keyboard.isDown(self._s):
                dy = +self._speed
            if self._e and self._keyboard.isDown(self._e):
                dx = +self._speed
            if self._w and self._keyboard.isDown(self._w):
                dx = -self._speed
            actor.move(dx, dy)        


class KeyboardNSEWToVectorCallback(Behaviour):
    """Calls a method with direction vector from ordinal directions according to the keyboard
    
    Set the n, s, e and w to the keys you want to move the actor. If you
    do not want any motion then set that direction to None. Set the speed
    to be the amount to move per keypress.
    
    This is useful when you want to move an object but you need to do
    some preprocessing first. This behaviour will allow you to capture the
    keypresses.
    
    """
    
    def __init__(self, method, event=serge.events.E_KEY_CLICKED, speed=1, 
            n=pygame.K_UP, s=pygame.K_DOWN, e=pygame.K_RIGHT, w=pygame.K_LEFT):
        """Initialise the behaviour"""
        super(KeyboardNSEWToVectorCallback, self).__init__()
        self._method = method
        self._event_method = 'isDown' if event == serge.events.E_KEY_DOWN else 'isClicked'
        self._speed = speed
        self._n = n
        self._s = s
        self._e = e
        self._w = w
        self._keyboard = serge.engine.CurrentEngine().getKeyboard()
        
    def __call__(self, world, actor, interval):
        """Perform the motion"""
        dy = dx = 0
        if self._n and getattr(self._keyboard, self._event_method)(self._n):
            dy = -self._speed
        if self._s and getattr(self._keyboard, self._event_method)(self._s):
            dy = +self._speed
        if self._e and getattr(self._keyboard, self._event_method)(self._e):
            dx = +self._speed
        if self._w and getattr(self._keyboard, self._event_method)(self._w):
            dx = -self._speed
        if dx or dy:
            self._method((dx, dy))

        
class KeyboardQuit(Behaviour):
    """Quit the game based on a keypress"""
    
    def __init__(self, key=pygame.K_ESCAPE):
        """Initialise the behaviour"""
        super(KeyboardQuit, self).__init__()
        self._key = key
        self._keyboard = serge.engine.CurrentEngine().getKeyboard()
        
    def __call__(self, world, actor, interval):
        """Check for the quit key"""
        if self._keyboard.isDown(self._key):
            self.log.info('Quit key pressed')
            serge.engine.CurrentEngine().stop()
            
            
class TimedCallback(Behaviour):
    """A callback that gets called at a certain interval"""
    
    def __init__(self, interval, callback):
        """Initialise the behaviour"""
        self.interval = interval
        self.callback = callback
        self.timer = 0.0
        self._number_calls = 0
        
    def __call__(self, world, actor, interval):
        """Check for the interval"""
        self.timer += interval
        if self.timer >= self.interval:
            self.timer -= self.interval            
            self.callback(world, actor, interval)
            self._number_calls += 1

class TimedOneshotCallback(TimedCallback):
    """A callback that gets called once and only once at an interval"""
    
    def __call__(self, world, actor, interval):
        """Check for the interval"""
        super(TimedOneshotCallback, self).__call__(world, actor, interval)
        if self._number_calls:
            self.record.pause()
            
class ParallaxMotion(Behaviour):
    """Move one object in relation to another"""

    def __init__(self, parent, (sx, sy)):
        """Initialise the ParallaxMotion"""
        self.parent = parent
        self.sx = sx
        self.sy = sy
        self.ox = parent.x
        self.oy = parent.y
        
    def __call__(self, world, actor, interval):
        """Perform the update"""
        dx = self.parent.x - self.ox
        dy = self.parent.y - self.oy
        #
        if dx or dy:
            actor.move(dx*self.sx, dy*self.sy)
            self.ox = self.parent.x
            self.oy = self.parent.y
            
class RemoveWhenOutOfRange(Behaviour):
    """Remove an actor from the world when it is out of a certain range"""

    def __init__(self, x_range, y_range):
        """Initialise the RemoveWhenOutOfRange"""
        super(RemoveWhenOutOfRange, self).__init__()
        self.space = serge.geometry.Rectangle(x_range[0], y_range[0], x_range[1]-x_range[0], y_range[1]-y_range[0])

    def __call__(self, world, actor, interval):
        """Check the actor is in range"""
        if not serge.geometry.Point(actor.x, actor.y).isInside(self.space):
            self.log.debug('Removed %s because it was out of range' % actor.getNiceName())
            world.scheduleActorRemoval(actor)
            return B_COMPLETED        
            
class ConstantVelocity(Behaviour):
    """Move an actor with a constant velocity"""
    
    def __init__(self, vx, vy):
        """Initialise the behaviour"""
        super(ConstantVelocity, self).__init__()
        #
        self.vx = vx
        self.vy = vy    
        
    def __call__(self, world, actor, interval):
        """Update the actor position"""
        actor.move(self.vx * interval/1000.0, self.vy * interval/1000.0)
        

