#!/usr/bin/env python

"""
My own wallpaper changer. 

I was not satisfied with the existing solutions so I made my own :)

Usage:
======
 
Simply launch it in the background. 
You can also put it among the startup applications.
"""

import os
import sys
import random

from time import sleep

import config as cfg

def print_info():
    li = [cfg.get_photo_dir_by_key(key) for key in cfg.ROTATOR_CHOICE]

    print "# Solo's wallpaper rotator 0.5"
    print "#", li
    print "# initial duration: {0} sec.".format(cfg.DURATION)


class WallpaperPicker:
    """Simple class for collecting images and picking one randomly."""
    
    def __init__(self):
        """To prevent picking the previous image."""
        self.prev = None
        
    def collect_images(self):
        """Collect images from _several_ directories."""
        li = []
        for key in cfg.ROTATOR_CHOICE:
            photo_dir = cfg.get_photo_dir_by_key(key)
            li.extend([os.path.join(photo_dir, x) for x in os.listdir(photo_dir) if x.lower().endswith('jpg')])
        self.images = li
        
    def get_nb_images(self):
        """Number of images."""
        return len(self.images)
    
    def get_first_image(self):
        """Get the first image."""
        return self.images[0]
    
    def get_random_image(self):
        """Get a random image from the list."""
        random.shuffle(self.images)
        img = random.choice(self.images)
        while img == self.prev:
            img = random.choice(self.images)
        self.prev = img
        
        return img
    
    def free_memory(self):
        """Don't keep the list in memory while waiting (sleep). After all,
        this list will be re-read each time."""
        del self.images


def main():
    print_info()
    
    wp = WallpaperPicker()

    no_of_monitors = 1

    #tested on 10.7 only ;)
    if sys.platform == 'darwin':
        from wallpapers.helper import macos as os_handler
        no_of_monitors = os_handler.get_no_of_monitors()
    else if sys.platform == 'win32':
        from wallpapers.helper import windows as os_handler
        no_of_monitors = os_handler.get_no_of_monitors()
    else:
        from wallpapers.helper import gnome as os_handler

    if cfg.SINGLE_WALLPAPER:
        no_of_monitors = 1

    while True:
        # if you modify the config file, this script doesn't have to be restarted
        reload(cfg)
        cfg.self_verify()
        
        # The list of images is re-read in each iteration because Wallpaper Downloader
        # is supposed to work parallelly. Thus, newly downloaded images will have a 
        # chance to appear on the desktop. 
        wp.collect_images()
        
        nb_images = wp.get_nb_images()
        
        if nb_images == 0:
            # there are no images in the directory => do nothing
            pass

        walls = []
        if nb_images == 1:
            # there is only one image => easy choice
            walls.append(wp.get_first_image())
            
        if nb_images > 1:
            for i in range(no_of_monitors):
                # there are several images => choose a different image than the previous pick
                walls.append(wp.get_random_image())


        print "Walls: {0}".format(walls) 	
        os_handler.set_wallpaper_image(walls)
            
        wp.free_memory()
            
        try:
            sleep(float(cfg.DURATION))
        except KeyboardInterrupt:
            sys.exit()

#############################################################################

if __name__ == "__main__":
    main()
