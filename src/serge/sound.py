"""The sound classes"""

import os

import pygame

import common
import serialize
import registry 
import events

#
# Initialise the pygame sound subsystem
pygame.mixer.init()
pygame.mixer.set_num_channels(common.NUM_AUDIO_CHANNELS)

class UnknownSound(Exception): """The sound was not found"""
class BadSound(Exception): """Could not load sound from"""


class AudioRegistry(registry.GeneralStore, common.EventAware):
    """Registry for audio"""
    
    def __init__(self):
        """Initialise the registry"""
        super(AudioRegistry, self).__init__()
        self._paused = False
        self.initEvents()
    
    def play(self, name, loops=0):
        """Play a sound"""
        self.getItem(name).play(loops)
    
    def pause(self):
        """Pause all sounds"""
        self._paused = True
        
    def unpause(self):
        """Unpause all sounds"""
        self._paused = False
    
    def toggle(self):
        """Toggle whether music or sound is playing or not"""
        if self.isPaused():
            self.unpause()
        else:
            self.pause()
        
    def isPaused(self):
        """Return True if we are paused"""
        return self._paused

    def update(self, interval):
        """Update the registry looking for events"""

    def isPlaying(self):
        """Return True if we are playing"""
                    
        
class Store(AudioRegistry):
    """Stores sounds"""
    
    def _registerItem(self, name, path):
        """Register the sound"""
        #
        # Load the sound
        try:
            sound = SoundItem(self._resolveFilename(path))
        except Exception, err:
            raise BadSound('Failed to load sound from "%s": %s' % (path, err))
        
        #
        # Remember the settings used to create the sound
        self.raw_items.append([name, path])
        self.items[name] = sound
        return sound
    
    def isPlaying(self):
        """Return True if we are playing"""
        return pygame.mixer.get_busy()
        
            
class MusicStore(AudioRegistry):
    """Stores music"""

    def __init__(self):
        """Initialise the store"""
        super(MusicStore, self).__init__()
        self.playing = None
        self._last_playing = None
        self.playlist = None
        
    def _registerItem(self, name, path):
        """Register the music"""
        if not os.path.isfile(self._resolveFilename(path)):
            raise BadSound('No music file "%s"' % self._resolveFilename(path))
        #
        # Remember the settings used to create the music
        self.raw_items.append([name, path])
        self.items[name] = MusicItem(self._resolveFilename(path))
        return self.items[name]

    def play(self, name, loops=0):
        """Play a sound"""
        super(MusicStore, self).play(name, loops)
        self.playing = self.getItem(name)
   
    def pause(self):
        """Pause all sounds"""
        super(MusicStore, self).pause()
        if self.playing:
            self.playing.pause()

    def unpause(self):
        """Unpause all sounds"""
        super(MusicStore, self).unpause()
        if self.playing:
            self.playing.unpause()

    def update(self, interval):
        """Update the registry looking for events"""
        super(MusicStore, self).update(interval)
        if not self.isPlaying() and self._last_playing:
            self.processEvent((events.E_TRACK_ENDED, self))
            #
            # If playing a playlist then move to the next one
            if self.playing and not self._paused and self.playlist:
                new = self.playlist.pop(0)
                self.play(new)
                self.playlist.append(new)
        #
        self._last_playing = self.isPlaying()

    def isPlaying(self):
        """Return True if we are playing"""
        return pygame.mixer.music.get_busy()

    def isPlayingSong(self, name):
        """Return True if the named song is playing"""
        return self.playing == self.getItem(name)
    
    def setPlaylist(self, item_list):
        """Set a playlist"""
        current = item_list.pop(0)
        item_list.append(current)
        self.play(current)
        self.playlist = item_list
        
    def fadeout(self, time):
        """Fadeout the currently playing track"""
        pygame.mixer.music.fadeout(int(time))
        self.playing = False

    def setVolume(self, volume):
        """Set the volume"""
        pygame.mixer.music.set_volume(volume)
        
    def getVolume(self):
        """Get the volume"""
        return pygame.mixer.music.get_volume()

           
class MusicItem(object):
    """Represents a music item"""
    
    def __init__(self, path):
        """Initialise the piece of music"""
        self._path = path   
        self._paused = False
    
    def play(self, loops=0):
        """Play the music"""
        pygame.mixer.music.stop()
        pygame.mixer.music.load(self._path)
        Music.playing = self
        self._paused = False
        if not Music.isPaused():
            pygame.mixer.music.play(loops)
            return True
        else:
            return False
    
    def pause(self):
        """Pause the music"""
        pygame.mixer.music.pause()
        self._paused = True
                
    def unpause(self):
        """Pause the music"""
        if Music.playing == self and self._paused:
            pygame.mixer.music.unpause()
        else:
            pygame.mixer.music.play()

    def stop(self):
        """Stop the music"""
        pygame.mixer.music.stop()
        Music.playing = None
        self._paused = False
    
    
class SoundItem(object):
    """Represents a sound item"""
    
    def __init__(self, path):
        """Initialise the sound"""
        self._sound = pygame.mixer.Sound(path)
        self._channel = None
        
    def play(self, loops=0):
        """Play the music"""
        if not Sounds.isPaused():
            self._channel = self._sound.play(loops)
            return True
        return False
    
    def pause(self):
        """Pause the music"""
        self._sound.pause()
        
    def unpause(self):
        """Pause the music"""
        self._sound.unpause()

    def stop(self):
        """Stop the music"""
        self._sound.stop()
        
    def set_volume(self, volume):
        """Set the volume"""
        self._sound.set_volume(volume)
        
    def get_volume(self):
        """Get the volume"""
        return self._sound.get_volume()
        
    def fadeout(self, time):
        """Fadeout the sound"""
        self._sound.fadeout(time)

    def isPlaying(self):
        """Return True if we are playing"""
        if self._channel and self._channel.get_busy():
            return True
        else:
            return False

            
Sounds = Store()
Music = MusicStore()
