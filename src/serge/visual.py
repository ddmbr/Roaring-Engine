"""Classes to handle sprites and other visual items"""

import pygame
import os
import copy
import re
import cairo
import rsvg

pygame.font.init()

import common
import serialize
import registry

class BadSprite(Exception): """The sprite was not loaded"""
class InvalidCell(Exception): """The sprite cell number was out of range"""
class BadScale(Exception): """An invalid scaling factor was used"""
class InvalidJustification(Exception): """The justification was not recognized"""
class NotAllFilesFound(Exception): """Didn't find all the files when looking for a multi cell from files"""
class BadFont(Exception): """The font was not loaded"""
class InvalidNameList(Exception): """The name list did not match the sprite given"""


log = common.getLogger('Visual')

class Store(registry.GeneralStore):
    """Stores sprites"""
    
    def _registerItem(self, name, path, w=1, h=1, framerate=0, running=False, rectangular=True, angle=0.0, zoom=1.0, loop=True):
        """Register a sprite"""
        #
        # Watch for special case h = -1 ... this is a multi cell
        if h == -1:
            return self.registerFromFiles(name, path, w, framerate, running, rectangular, angle, zoom, loop)
        #
        # Reality heighteck
        if zoom <= 0.0:
            raise BadScale('The zoom factor for sprite %s was not >= 0' % name)
        #
        # Special case of no filename - we want to specify this layer
        if path != '':
            #
            # Load the image and work out the dimensions based on the number of cells
            # wide and high
            try:
                if path[-3:] != 'svg':
                    image = pygame.image.load(self._resolveFilename(path))
                elif path[-3:] == 'svg':
                    print 'svg file type detected'
                    svg_graphics = rsvg.Handle(self._resolveFilename(path))
                    size = svg_graphics.get_dimension_data()
                    image = pygame.Surface((size[0], size[1]))
                    pixels = pygame.surfarray.pixels2d(image)
                    cairo_surface = cairo.ImageSurface.create_for_data(pixels.data, cairo.FORMAT_RGB24, size[0], size[1])
                    ctx = cairo.Context(cairo_surface)
                    svg_graphics.render_cairo(ctx)
            except Exception, err:
                raise BadSprite('Failed to load sprite from "%s": %s' % (path, err))
            #
            s = self._registerImage(name, image, w, h, framerate, running, rectangular, angle, zoom, loop)
        else:
            s = self.items[name] = None
        #
        # Remember the settings used to create the sprite
        self.raw_items.append([name, path, w, h, framerate, running, rectangular, angle, zoom, loop])
        return s

    def _registerImage(self, name, image, w, h, framerate, running, rectangular, angle, zoom, loop):
        """Register an image"""
        #
        if zoom != 1.0:
            image = pygame.transform.smoothscale(image, (int(image.get_width()*zoom), int(image.get_height()*zoom)))
        if angle != 0.0:
            image = pygame.transform.rotate(image, angle)
        #
        width = image.get_width()/w        
        height = image.get_height()/h
        #
        # Now load as a sprite sheet
        s = Sprite()
        #
        try:
            s.setImage(image, (width, height), framerate, running)
        except Exception, err:
            raise BadSprite('Failed to create sprite %s: %s' % (name, err))
        #
        # Set properties
        s.framerate = framerate
        s.running = running
        s.rectangular = rectangular   
        s.loop = loop
        s.name = name
        #
        self.items[name] = s         
        #
        return s
    
    def registerFromFiles(self, name, path, number, framerate=0, running=False, rectangular=True, angle=0.0, 
                            zoom=1.0, start=1, loop=True):
        """Register a multi cell sprite from a number of files
        
        The path should be a string with a single numerical substitution.
        We will pass the numbers 1..number to this substitution to find
        the names of the files.
        
        """
        #
        # Generate a composite image - load the first one to find the size
        try:
            image = pygame.image.load(self._resolveFilename(path % start))
        except Exception, err:
            raise BadSprite('Failed to load multi cell sprite from "%s": %s' % (path, err))
        #
        # Get size
        width = image.get_width()        
        height = image.get_height()
        #
        # Now create a canvas to load all the files onto
        canvas = pygame.Surface((number*width, height), pygame.SRCALPHA, 32)
        for i in range(1, number+1):
            try:
                image = pygame.image.load(self._resolveFilename(path % (i+start-1)))
            except Exception, err:
                raise NotAllFilesFound('Failed to load multi cell sprite from "%s": %s' % (path, err))
            canvas.blit(image, ((i-1)*width, 0))
        #
        # Ok, now create as if normal
        s = self._registerImage(name, canvas, number, 1, framerate, running, rectangular, angle, zoom, loop)
        #
        # Special case of h = -1 to trigger logic in the registerItem method when we are recovering from
        # a serialize
        self.raw_items.append([name, path, number, -1, framerate, running, rectangular, angle, zoom, loop])
        #
        return s

    def registerMultipleItems(self, names, path, w, h=1, rectangular=True, angle=0.0, zoom=1.0):
        """Register a number of sprites from a single image
        
        The image must be a horizontal row of sprites and you must provide
        a list of names the same size as the row of sprites. Each other sprites
        will be created.
        
        """
        #
        # Reality check on the names
        if len(names) != w*h:
            raise InvalidNameList('Name list length, %d, does not match sprite width, %d, (%s)' % (
                len(names), w, names))
        if len(names) != len(set(names)):
            raise InvalidNameList('Name list contains duplcate names (%s)' % names)
        #
        # Split into cells using a temporary sprite
        temp = self._registerItem('__TEMP__', path, w, h)
        #
        # Now get the individual images out
        for idx, name in enumerate(names):
            self._registerImage(name, temp.cells[idx], 1, 1, 0, False, rectangular, angle, zoom, False)
        #
        # Clean up
        self.removeItem('__TEMP__')
    
    def registerItemsFromPattern(self, pattern, prefix='', w=1, h=1, framerate=0, running=False, rectangular=True, angle=0.0, zoom=1.0, loop=True):
        """Register all items matching a certain regular expression"""
        items = [item for item in os.listdir(self._resolveFilename('')) if re.match(pattern, item)]
        for item in items:
            self.registerItem('%s%s' % (prefix, os.path.splitext(item)[0]), 
                item, w, h, framerate, running, rectangular, angle, zoom, loop)
        
         
Register = Store() # Legacy name
Sprites = Register


class Drawing(object):
    """Represents something to draw on the screen"""

    def __init__(self):
        """Initialise the drawing"""
        self._alpha = 1.0
        self.width = 0.0
        self.height = 0.0
        self.zoom = 1.0
        self.angle = 0.0
        self.horizontal_flip = False
        self.vertical_flip = False
            
    def setScale(self, scale):
        """Set the scaling to a certain factor"""
        self.scaleBy(scale/self.zoom)

    def scaleBy(self, factor):
        """Scale the image by a factor"""
        raise NotImplementedError('scaleBy not implemented on %s' % self)
            
    def setAngle(self, angle):
        """Set the rotation to a certain angle"""
        raise NotImplementedError('setAngle not implemented on %s' % self)
    
    def getAngle(self):
        """Return the current angle"""
        return self.angle

    def rotateBy(self, angle):
        """Rotate by a certain amount"""
        self.setAngle(self.getAngle()+angle)
        
    def flipHorizontal(self):
        """Flip the drawing horizontally"""
        raise NotImplementedError('flipHorizontal not implemented on %s' % self)
        
    def flipVertical(self):
        """Flip the drawing vertically"""
        raise NotImplementedError('flipVertical not implemented on %s' % self)
    
    ### Rendering ###
        
    def renderTo(self, milliseconds, surface, (x, y)):
        """Render to a surface"""
        raise NotImplementedError('renderTo not implemented on %s' % self)

    def setAlpha(self, alpha):
        """Set the overall alpha"""
        raise NotImplementedError('setAlpha not implemented on %s' % self)

    def _setAlphaForSurface(self, surface, alpha):
        """Set the alpha for a surface"""
        #
        # (Not quite sure about all of this!)
        # Try to set the alpha and then if this fails drop back to slow method
        surface.set_alpha(alpha*255)
        if surface.get_at((0,0))[3] == alpha*255:
            return
        #
        size = surface.get_size()
        for y in xrange(size[1]):
            for x in xrange(size[0]):
                r,g,b,a = surface.get_at((x,y))
                surface.set_at((x,y),(r,g,b,int(a*alpha)))
        return surface

    @property
    def alpha(self): return self._alpha
    @alpha.setter
    def alpha(self, alpha): self.setAlpha(alpha)
    
    ### Copying ###
    
    def getCopy(self):
        """Return a copy"""
        return copy.copy(self)

    def setSize(self, width, height):
        """Set the size of the drawing directly"""
        raise NotImplementedError('setSize not implemented on %s' % self)


class SurfaceDrawing(Drawing):
    """A visual object that renders to a surface. 
    
    You can create an instance of this class and then write to its surface
    or use this as a base class for your own class that will write
    the surface.
    
    """

    def __init__(self, width, height):
        """Initialise the surface"""
        super(SurfaceDrawing, self).__init__()
        self.width = width
        self.height = height
        self.clearSurface()
            
    def getSurface(self):
        """Return our surface"""
        return self.surface

    def clearSurface(self):
        """Clear the surface"""
        return self.setSurface(pygame.Surface((self.width, self.height), pygame.SRCALPHA, 32))

    def setSurface(self, surface):
        """Update our surface"""
        self.raw_image = self.surface = surface
        self._updateDimensions()
        return self.surface
        
    def renderTo(self, milliseconds, surface, (x, y)):
        """Render to a surface"""
        img = self.getSurface()
        surface.blit(img, (x-img.get_width()/2, y-img.get_height()/2))

    def scaleBy(self, factor):
        """Scale the image by a factor"""
        if factor <= 0:
            raise BadScale('Scaling factor must be >= 0')
        self.zoom *= factor
        img = self.raw_image
        self.surface = pygame.transform.smoothscale(img, (int(img.get_width()*self.zoom), int(img.get_height()*self.zoom)))
        self._updateDimensions()
        
    def setAngle(self, angle):
        """Change the angle - returning the amount by which the sprite has shifted"""
        self.angle = angle
        self.surface = pygame.transform.rotate(self.raw_image, self.angle)
        self._updateDimensions()

    def _updateDimensions(self):
        """Update the dimensions of the drawing"""
        self.width = self.surface.get_width()
        self.height = self.surface.get_height()
        self.cx = self.width/2
        self.cy = self.height/2
        self.radius = max(self.width, self.height)/2   

    def setSize(self, width, height):
        """Set the size of the drawing directly"""
        img = self.raw_image
        self.surface = pygame.transform.smoothscale(img, int(width), int(height))
        self._updateDimensions()
        
        
class Sprite(Drawing):
    """An object that gets drawn on the screen"""
    
    #
    # This is the function used to rotate the sprite. You can change this to "rotate"
    # to get non-filtered rotations
    smooth_rotate = lambda self, img, angle, scale : pygame.transform.rotozoom(img, angle, scale)
    base_rotate = lambda self, img, angle, scale : pygame.transform.rotate(img, angle)
    #
    rotate = smooth_rotate
    
    # Set the following to True to allow caching of rotations of a sprite to the given number of degrees
    cache_rotations = False
    cache_granularity = 1.0 
    
    def getCopy(self):
        """Return a copy of this sprite"""
        new = self.__class__()
        new.setImage(self.raw_image, (self.width, self.height), self.framerate, self.running, self.loop)
        return new

    def getSurface(self):
        """Return the current surface"""
        return self.cells[self.current_cell]

    def setAlpha(self, alpha):
        """Set the overall alpha"""
        self.setCells()
        for idx, cell in enumerate(self.cells):
            self._setAlphaForSurface(cell, alpha)
        self._alpha = alpha

    def setImage(self, image, (width, height), framerate=0, running=False, loop=True):
        """Set the image of this sprite"""
        #
        # Store cells of the image for speed - use of the cache is determined by the
        # cache_rotations property
        self._cell_cache = {}
        #
        # Store raw image
        self.raw_image = image
        self.width = self.raw_width = width
        self.height = self.raw_height = height
        self.cx = self.raw_cx = width/2
        self.cy = self.raw_cy= height/2
        #
        self.framerate = framerate
        self.frame_time = 0 if framerate == 0 else 1000.0/framerate
        self.running = running
        self.loop = loop
        self.last_time = 0
        self.direction = 1
        self.zoom = 1.0
        self.angle = 0.0
        self.fixed_size = None
        #
        self.setCells()
        self.current_cell = 0
        self._alpha = 1.0
        
    ### Cells ###
        
    def setCells(self):
        """Set the cells of the animation"""
        self.cells = []
        #
        # Have we cached this set of cells
        if self.cache_rotations:
            granular_angle = (self.angle//self.cache_granularity)*self.cache_granularity
            try:
                self.cells = self._cell_cache[granular_angle]
            except KeyError:
                # Oh, well - not in the cache after all
                pass
        #
        # Make cells
        if not self.cells:
            rows = self.raw_image.get_height()/self.raw_height
            cols = self.raw_image.get_width()/self.raw_width
            #
            raw_image = self.raw_image.copy()
            for row in range(rows):
                for col in range(cols):
                    r = pygame.Rect(col*self.raw_width, row*self.raw_height, self.raw_width, self.raw_height)
                    img = raw_image.subsurface(r)
                    if self.horizontal_flip or self.vertical_flip:
                        img = pygame.transform.flip(img, self.horizontal_flip, self.vertical_flip)
                    if self.zoom != 1.0:
                        img = pygame.transform.smoothscale(img, (int(img.get_width()*self.zoom), int(img.get_height()*self.zoom)))
                    elif self.fixed_size:
                        img = pygame.transform.smoothscale(img, self.fixed_size)
                    if self.angle != 0.0:
                        img = self.rotate(img, self.angle, 1.0)
                    self.cells.append(img)
        #
        if self.cells:
            self.width = self.cells[0].get_width()
            self.height = self.cells[0].get_height()
            self.cx = self.width/2
            self.cy = self.height/2
            self.radius = max(self.width, self.height)/2
        #
        if self.cache_rotations:
            self._cell_cache[granular_angle] = self.cells

    def setSize(self, width, height):
        """Set the size of the drawing directly"""
        self.fixed_size = (int(width), int(height))
        self.zoom = 1.0
        self.setCells()
            
    def setCell(self, number):
        """Set the current cell number"""
        if 0 <= number < len(self.cells):
            self.current_cell = number
        else:
            raise InvalidCell('Cell number %d is out of range for this sprite' % number)
        
    def getCell(self):
        """Return the current cell number"""
        return self.current_cell
    
    def getNumberOfCells(self):
        """Return the number of animation cells"""
        return len(self.cells)
        
    ### Deformations ###
    
    def scaleBy(self, factor):
        """Scale the image by a factor"""
        if factor <= 0:
            raise BadScale('Scaling factor must be >= 0')
        self.zoom *= factor
        self.setCells()

    def setAngle(self, angle):
        """Change the angle - returning the amount by which the sprite has shifted"""
        self.angle = angle
        self.setCells()

    def flipHorizontal(self):
        """Flip the drawing horizontally"""
        self.horizontal_flip = not self.horizontal_flip
        self.setCells()
        
    def flipVertical(self):
        """Flip the drawing vertically"""
        self.vertical_flip = not self.vertical_flip    
        self.setCells()

    ### Rendering ###
        
    def renderTo(self, milliseconds, surface, (x, y)):
        """Render to a surface"""
        #
        # Update current frame
        if self.framerate and self.running:
            self.last_time += milliseconds
            if self.last_time >= self.frame_time:
                self.last_time -= self.frame_time
                self.current_cell += self.direction
                if self.current_cell <= 0:
                    self.current_cell = 0
                    self.direction = 1
                    if not self.loop:
                        self.running = False
                elif self.current_cell >= len(self.cells)-1:
                    self.current_cell = len(self.cells)-1
                    self.direction = -1       
                    if not self.loop:
                        self.running = False
        #
        # Draw to the surface
        surface.blit(self.cells[self.current_cell], (x, y))

    def resetAnimation(self, running):
        """Reset the animation to the begining"""
        self.setCell(0)
        self.direction = 1
        self.running = running
               
class Text(Drawing):
    """Some text to display"""
    
    def __init__(self, text, colour, font_name='DEFAULT', font_size=12, justify='center'):
        """Initialise the text"""
        super(Text, self).__init__()
        # 
        # Hack - see below
        self._actor_parent = None
        #
        self.colour = colour if len(colour) == 4 else (colour + (255,))
        self.text = text
        self.font_size = font_size
        self.angle = 0.0
        self.font_path = Fonts.getItem(font_name)
        self.font = pygame.font.Font(self.font_path, font_size)
        self.setText(text)
        self.justify = justify
        
    def setJustify(self, justify):
        """Set the justification"""
        setting = justify.lower()
        if setting not in ('left', 'center'):
            raise InvalidJustification('Justification not recognized (%s)' % justify)
        self.justify = setting
        
    def setText(self, text):
        """Set our text"""
        #
        # Break into lines and then render each one
        if text == '':
            text = ' '
        lines = text.splitlines()
        #
        # Find out how wide to make our surface
        max_length, long_line = max([(len(line), line) for line in lines])       
        test_text = self.font.render(long_line, True, self.colour)
        width = test_text.get_width()
        height = self.font.get_height()
        #
        # Now make a surface
        self.surface = pygame.Surface((width, height*len(lines)), pygame.SRCALPHA, 32)
        #
        # And write all our text
        for idx, line in enumerate(lines):
            self.surface.blit(self.font.render(line, True, self.colour), (0, height*idx))
        #
        if self.angle != 0:
            self.surface = pygame.transform.rotate(self.surface, self.angle)
        self.width = self.surface.get_width()
        self.height = self.surface.get_height()
        #
        # Hack to get the actor to spot that we updated our width
        if self._actor_parent:
            self._actor_parent.resizeTo(self.width, self.height)
        #
        self.text = text

    def setColour(self, colour):
        """Set the colour"""
        self.colour = colour
        self.setText(self.text)
                
    def setFontSize(self, font_size):
        """Set our font size"""
        self.font_size = int(font_size)
        self.font = pygame.font.Font(self.font_path, int(font_size))
        self.setText(self.text)

    def setAlpha(self, alpha):
        """Set our alpha"""
        self.setText(self.text)
        self._setAlphaForSurface(self.surface, alpha)
        self._alpha = alpha
        
    def renderTo(self, milliseconds, surface, (x, y)):
        """Render to a surface"""
        if self.justify == 'left':
            surface.blit(self.surface, (x+self.width/2, y+self.height/2))
        else:
            surface.blit(self.surface, (x, y))
        
    def setAngle(self, angle):
        """Rotate our sprite by a certain angle"""
        self.angle = angle
        self.setText(self.text)
        
    def scaleBy(self, scale):
        """Scale our sprite by a certain certain amount"""
        self.setFontSize(self.font_size*scale)
        
        
### Fonts ###


class FontStore(registry.GeneralStore):
    """A store for fonts"""
    
    def registerItem(self, name, path):
        """Register a font"""
        #
        # Special case for DEFAULT - we allow multiple registrations of
        # this one
        if name == 'DEFAULT' and name in self.items:
            self.removeItem('DEFAULT')
        super(FontStore, self).registerItem(name, path)
        
    def _registerItem(self, name, path):
        """Register the font"""
        #
        # Try to load a font - we are going to discard this but it is a good
        # check to see if we will be able to create a font later
        real_path = path
        try:
            _ = pygame.font.Font(real_path, 12)
        except Exception, err:
            #
            # Try with actual path
            real_path = self._resolveFilename(path)
            try:
                _ = pygame.font.Font(real_path, 12)
            except Exception, err:
                raise BadFont('Failed to load font from "%s": %s' % (path, err))
        #
        # Remember the settings used to create the sound
        self.raw_items.append([name, real_path])
        self.items[name] = real_path
        return real_path

    def clearItems(self):
        """Clear the items
        
        Leaves the DEFAULT item in there if it is there.
        
        """
        try:
            default = self.getItem('DEFAULT')
        except registry.UnknownItem:
            default = None
        super(FontStore, self).clearItems()
        if default:
            self.registerItem('DEFAULT', default)
        
Fonts = FontStore()
Fonts.registerItem('DEFAULT', pygame.font.get_default_font())

