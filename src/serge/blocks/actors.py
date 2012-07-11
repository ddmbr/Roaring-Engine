"""Blocks to help with actors"""

import serge.actor
import serge.engine
import serge.actor
import serge.events


class InvalidMenu(Exception): """The menu was not valid"""
class InvalidMenuItem(Exception): """The menu item was not understood"""



class ScreenActor(serge.actor.CompositeActor):
    """An actor to represent the logic associated with a screen of the game
    
    This actor is useful when encapsulating the logic associated with a specific
    screen in the game. The actor has useful properties and methods that
    make it easy to manage the logic.
    
    """

    def __init__(self, *args, **kw):
        """Initialise the ScreenActor"""
        super(ScreenActor, self).__init__(*args, **kw)
        
    def addedToWorld(self, world):
        """The actor was added to the world"""
        super(ScreenActor, self).addedToWorld(world)
        self.world = world
        self.engine = serge.engine.CurrentEngine()
        self.keyboard = self.engine.getKeyboard()
        self.mouse = self.engine.getMouse()
        self.camera = self.engine.getRenderer().getCamera()
        self.broadcaster = serge.events.getEventBroadcaster()
        

class RepeatedVisualActor(serge.actor.Actor):
    """An actor that shows multiple copies of a visual representation
    
    This actor is useful for showing the number of lives or missiles
    etc in a game.
    
    """

    def __init__(self, tag, name=None, repeat=5, spacing=10, orientation='horizontal'):
        """Initialise the RepeatedVisualActor"""
        super(RepeatedVisualActor, self).__init__(tag, name)
        self._repeat = repeat
        self._spacing = spacing
        self._current = repeat
        self._orientation = orientation

    def _resetVisual(self):
        """Reset the visual item on the center point
        
        We need to override this because our size is not determined by our visual
        
        """
        #
        # Adjust our location so that we are positioned and sized appropriately
        cx, cy, _, _ = self.getSpatialCentered()
        #
        if self._orientation == 'horizontal':
            self.setSpatialCentered(cx, cy, 
                self._visual.width + self._spacing*(self._repeat-1), self._visual.height)
        else:
            self.setSpatialCentered(cx, cy, 
                self._visual.width, self._visual.height + self._spacing*(self._repeat-1))
        #
        # Here is a hack - sometimes the visual width changes and we want to update our width
        # so we let the visual know about us so it can update our width. This is almost 
        # certainly the wrong thing to do, but we have some tests in there so hopefully
        # the right thing becomes obvious later!
        self._visual._actor_parent = self
        
    def renderTo(self, renderer, interval):
        """Render ourself to the given renderer"""
        if self._visual:
            layer = renderer.getLayer(self.layer)
            camera = renderer.camera
            if layer.static:
                ox, oy = self.getOrigin()
            elif camera.canSee(self):
                ox, oy = camera.getRelativeLocation(self)
            else: 
                return # Cannot see me
            if self.layer:
                for i in range(self._current):
                    if self._orientation == 'horizontal':
                        x, y = (ox + i*self._spacing, oy)
                    else:
                        x, y = (ox, oy + i*self._spacing)
                    self._visual.renderTo(interval, renderer.getLayer(self.layer).getSurface(), (x, y))

    def reduceRepeat(self, amount=1):
        """Reduce the repeat by a certain amount"""
        self.setRepeat(self._current - amount)
        
    def increaseRepeat(self, amount=1):
        """Increase the repeat by a certain amount"""
        self.setRepeat(self._current + amount)
        
    def getRepeat(self):
        """Return the current repeat"""
        return self._current

    def setRepeat(self, value):
        """Set the current repeat"""
        if self._current != value:
            self._current = value
            #
            # Reset the visual size
            ox, oy, w, h = self.getSpatial()
            if self._orientation == 'horizontal':
                w = self._visual.width + self._spacing*(self._current-1)
            else:
                h = self._visual.height + self._spacing*(self._current-1)
            self.setSpatial(ox, oy, w, h)
            self.log.debug('New spatial = %s' % self.getSpatial())
        
    def resetRepeat(self):
        """Reset the repeat to the initial value"""
        self.setRepeat(self._repeat)
        
        
class FormattedText(serge.actor.Actor):
    """A text display that can be formatted"""

    def __init__(self, tag, name, format, colour, font_name='DEFAULT', font_size=12, justify='center', **kw):
        """Initialise the text"""
        super(FormattedText, self).__init__(tag, name)
        self.visual = serge.visual.Text('', colour, font_name, font_size, justify)
        self.format = format
        self.values = kw
        self.updateText()
        
    def updateText(self):
        """Update our text"""
        self.visual.setText(self.format % self.values)

    def setValue(self, name, value):
        """Set the value"""
        self.values[name] = value
        self.updateText()
            
    def getValue(self, name):
        """Get the values"""
        return self.values[name]

class NumericText(FormattedText):
    """A helper actor to display some text with a single number in there"""

    def __init__(self, *args, **kw):
        """Initialise the text"""
        super(NumericText, self).__init__(*args, **kw)
        
    def updateText(self):
        """Update our text"""
        self.visual.setText(self.format % self.values['value'])

    @property
    def value(self): return self.getValue('value')
    @value.setter
    def value(self, v): self.setValue('value', v)


class StringText(FormattedText):
    """A helper actor to display some text with text in there"""

    def __init__(self, tag, name, text, format='%s', colour=(255, 255, 255), font_name='DEFAULT', font_size=12, justify='center'):
        """Initialise the text"""
        super(StringText, self).__init__(tag, name, format, colour, font_name, font_size, justify, value=text)
        
    def updateText(self):
        """Update our text"""
        self.visual.setText(self.format % self.values['value'])

    @property
    def value(self): return self.getValue('value')
    @value.setter
    def value(self, v): self.setValue('value', v)


class MuteButton(serge.actor.Actor):
    """A button to mute sound"""

    def __init__(self, sprite_name, layer_name, mute_sound=True, mute_music=True, alpha=1.0):
        """Initialise the button"""
        super(MuteButton, self).__init__('mute-button', 'mute-button')
        self.mute_sound = mute_sound
        self.mute_music = mute_music
        self.setSpriteName(sprite_name)
        self.setLayerName(layer_name)
        self.visual.setAlpha(alpha)
        self.linkEvent(serge.events.E_LEFT_CLICK, self.toggleSound)
        
    def toggleSound(self, obj=None, arg=None):
        """Clicked on the button"""
        if self.mute_sound:
            serge.sound.Sounds.toggle()
        if self.mute_sound:
            serge.sound.Music.toggle()
        self.visual.setCell(1 if self.visual.getCell() == 0 else 0)


class ToggledMenu(serge.actor.MountableActor):
    """Implements a menu of options that can be toggled"""

    def __init__(self, tag, name, items, layout, default, on_colour, off_colour, 
                    width=100, height=100, callback=None, font_colour=(255, 255, 255, 255), 
                    font_name='DEFAULT', font_size=12):
        """Initialise the ToggledMenu"""
        super(ToggledMenu, self).__init__(tag, name)
        #
        # Reality check
        if not items:
            raise InvalidMenu('Menu must have at least one item in it')
        if len(set(items)) != len(items):
            raise InvalidMenu('Menu cannot have duplicates in it (%s)' % (', '.join(items)))         
        #
        # Setup the menu
        self.mountActor(layout, (0, 0))
        self.on_colour = on_colour
        self.off_colour = off_colour
        self.callback = callback
        self.layout = layout
        #
        self._setupMenu(items, width, height, font_colour, font_name, font_size)
        self.selectItem(default)

    def _setupMenu(self, items, width, height, font_colour, font_name, font_size):
        """Setup all the menu items"""
        self._menu_items = {}
        self.items = items
        self._selection = None
        #
        for idx, item in enumerate(items):
            new_item = serge.actor.Actor(('%s-menuitem' % self.name), '%s-item-%s' % (self.name, idx))
            new_item.visual = serge.blocks.visualblocks.RectangleText(item, font_colour, (width, height), self.off_colour,
                font_size=font_size, font_name=font_name)
            self._menu_items[item] = new_item
            self.layout.addActor(new_item)
            new_item.linkEvent(serge.events.E_LEFT_CLICK, self._itemClick, item)
        
    def selectItem(self, name):
        """Select an item by name"""
        #
        # Don't select if already selected
        if name == self._selection:
            return
        #
        try:
            the_item = self._menu_items[name]
        except KeyError:
            raise InvalidMenuItem('Menu item "%s" not found in menu %s' % (name, self.getNiceName()))
        #
        # Highlight items
        for item in self._menu_items.values():
            item.visual.rect_visual.colour = self.on_colour if item is the_item else self.off_colour
        #
        self._selection = name
        if self.callback:
            self.callback(self, name)

    def selectItemIndex(self, index):
        """Select an item by its index"""
        try:
            name = self.items[index]
        except IndexError:
            raise InvalidMenuItem('Index %s is outside the range of menu %s' % (index, self.getNiceName()))
        self.selectItem(name)
        
    def getSelection(self):
        """Return the current selection"""
        return self._selection
        
    def getSelectionIndex(self):
        """Return the current selection index"""
        return self.items.index(self._selection)
        
    def _itemClick(self, obj, name):
        """Clicked on an item"""
        self.selectItem(name)     


class AnimateThenDieActor(serge.actor.Actor):
    """An actor that shows its animation and then is removed from the world"""

    def __init__(self, tag, name, sprite_name, layer_name, parent=None):
        """Initialise the AnimateThenDieActor
        
        If the parent is specified then we will be moved to the location of the parent
        
        """
        super(AnimateThenDieActor, self).__init__(tag, name)
        #
        self.parent = parent
        self.setSpriteName(sprite_name)
        self.setLayerName(layer_name)
        
    def addedToWorld(self, world):
        """Added the actor to the world"""
        super(AnimateThenDieActor, self).addedToWorld(world)
        #
        if self.parent:
            self.moveTo(self.parent.x, self.parent.y)
            
    def updateActor(self, interval, world):
        """Update the actor"""
        if not self.visual.running:
            # Ok, run its course
            world.scheduleActorRemoval(self)
            
class FPSDisplay(NumericText):
    """Displays the current FPS on the screen"""
    
    def __init__(self, x, y, font_colour, font_size, font_name='DEFAULT'):
        """Initialise the FPS display"""
        super(FPSDisplay, self).__init__('fps', 'fps', 'FPS: %5.2f', colour=font_colour, font_size=font_size,
            value=0, font_name=font_name)
        self.setLayerName('ui')
        self.moveTo(x, y)  
        self.engine = serge.engine.CurrentEngine()
    def updateActor(self, interval, world):
        """Update the actor"""
        self.value = self.engine.getStats().average_frame_rate
