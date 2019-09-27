#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

'''
(c) 2017 Miguel Colom
http://mcolom.info
'''

import os
import os.path
from tkinter import filedialog
import numpy as np
import matplotlib.pyplot as plt
import smos.smos as smos

# Configure keys
USE_D_KEY_TO_OPEN = True
#
OPEN_KEY = 'd' if USE_D_KEY_TO_OPEN else 'q'
SAVE_KEY = 'a'
GENERATE_KEY = 'enter'

# Constants
lamb = 299792458 / 1413e6
q = 2

class AntennasSpatial(object):
    '''
    Main class
    '''
    def __init__(self):
        # Print configuration keys
        self.print_keys()

        # cd to the directory of the script
        abspath = os.path.abspath(__file__)
        dname = os.path.dirname(abspath)
        os.chdir(dname)

        # List of points
        self.points_spatial = set()
        self.points_freq = dict()

        self.limit = 10.0 # Set limits
        self.step = 0.25 # Step

        # Create spatial and frequential figures
        self.create_spatial_figure()
        self.create_freq_figure()

        # State
        self.control_pressed = False
        self.dragging = False
        self.drag_start_coord = None
        self.picked_artist = None

        # Connect events
        self.fig_spatial.canvas.mpl_connect('pick_event', self.onpick)
        self.fig_spatial.canvas.mpl_connect('motion_notify_event', self.onMove)
        self.fig_spatial.canvas.mpl_connect('button_press_event', self.onClick)
        self.fig_spatial.canvas.mpl_connect('button_release_event', self.onClickRelease)
        self.fig_spatial.canvas.mpl_connect('key_press_event', self.onkeyPress)
        self.fig_spatial.canvas.mpl_connect('key_release_event', self.onkeyReleased)
        self.fig_spatial.canvas.mpl_connect('close_event', self.onClose)
        #
        self.fig_freq.canvas.mpl_connect('close_event', self.onClose)

        # And show
        plt.show()

    @staticmethod
    def print_keys():
        '''
        Print keys configuration
        '''
        print("Key configuration:")
        print("\t- OPEN: {}".format(OPEN_KEY))
        print("\t- SAVE: {}".format(SAVE_KEY))
        print("\t- GENERATE: {}".format(GENERATE_KEY))
        print()

    def create_spatial_figure(self):
        '''
        Create spatial figure
        '''
        self.fig_spatial = plt.figure(1)

        self.fig_spatial.set_figheight(8) # Maintain aspect ratio
        self.fig_spatial.set_figwidth(8)

        self.ax_spatial = self.fig_spatial.add_subplot(111)

        self.ax_spatial.set_xlim(-self.limit, self.limit)
        self.ax_spatial.set_ylim(-self.limit, self.limit)

        self.ax_spatial.set_xticks(np.arange(-self.limit, self.limit, 1))
        self.ax_spatial.set_yticks(np.arange(-self.limit, self.limit, 1))
        self.ax_spatial.grid(True)

        self.ax_spatial.set_title('Antennas spatial configuration')

    def create_freq_figure(self):
        '''
        Create Fourier figure
        '''
        self.fig_freq = plt.figure(2)
        self.ax_freq = self.fig_freq.add_subplot(111)
        self.ax_freq.grid(True)
        self.ax_freq.set_title('Antennas Fourier')

        self.fig_freq.set_figheight(8) # Maintain aspect ratio
        self.fig_freq.set_figwidth(8)

    def clear_spatial(self):
        '''
        Remove all antennas
        '''
        self.points_spatial = set()
        self.ax_spatial.artists = []
        self.fig_spatial.canvas.draw()

    def clear_freq(self):
        '''
        Remove all frequencies
        '''
        self.ax_freq.artists = []
        self.fig_freq.canvas.draw()

    def generate_freq(self):
        '''
        Compute and draw frequential antenna pattern
        '''
        self.clear_freq()
        self.points_freq = smos.get_baselines_dict(self.points_spatial)
        
        # Draw circles representing antennas
        for key in self.points_freq:
            x, y = smos.key2freq(key)
            
            # From distance between antennas to sampling freqs.
            x = x * q / lamb
            y = y * q / lamb
            
            circle = plt.Circle((x, y), lamb/2, color='b', alpha=0.5)
            self.ax_freq.add_artist(circle)

            text_artist = plt.Text(x, y, self.points_freq[key], fontsize=10)
            self.ax_freq.add_artist(text_artist)

    @staticmethod
    def open_file_dialog():
        '''
        GUI: show open dialog
        '''
        opts = {}
        opts['filetypes'] = [('text files', ('.txt'))]
        return filedialog.askopenfilename(**opts)

    @staticmethod
    def save_file_dialog():
        '''
        GUI: show save dialog
        '''
        return filedialog.asksaveasfile()

    def load_file(self, filename):
        '''
        Load the given filename with the antennas spatial configuration
        '''
        antennas = smos.load_spatial(filename)

        self.points_spatial = set()
        for x, y in antennas:
            self.points_spatial.add((x, y))
                
        # Create and add all artists
        for point in self.points_spatial:
            x, y = point
            circle = plt.Circle((x, y), lamb/2, color='b', alpha=0.5, picker=True)
            self.ax_spatial.add_artist(circle)

    def save_file(self, f):
        '''
        Save the current spatial pattern
        '''
        for coord in self.points_spatial:
            f.write("{}, {}\n".format(coord[0], coord[1]))

    def apply_step(self, x, y):
        '''
        Apply the step to the given coordinates
        '''
        if not self.step:
            return x, y

        sx = np.round(x / self.step) * self.step
        sy = np.round(y / self.step) * self.step
        return sx, sy

    #def onpick(self, circle, mouse_event):
    def onpick(self, event):
        '''
        GUI: on pick event
        '''
        self.picked_artist = event.artist
        self.drag_start_coord = event.artist.center
        self.dragging = True

    def onClick(self, event):
        '''
        GUI: on click event
        '''
        if not event.xdata or not event.ydata:
            return

        if event.button == 1 and self.control_pressed:
            x, y = self.apply_step(event.xdata, event.ydata)

            if (x, y) in self.points_spatial:
                return # Point already exists in that position

            self.points_spatial.add((x, y))
            circle = plt.Circle((x, y), lamb/2, color='b', alpha=0.5, picker=True)
            self.ax_spatial.add_artist(circle)
            circle.figure.canvas.draw()

    def onMove(self, event):
        '''
        GUI: on move event
        '''
        if self.dragging:
            x, y = self.apply_step(event.xdata, event.ydata)
            if (x, y) in self.points_spatial:
                return

            self.picked_artist.center = (x, y)
            self.fig_spatial.canvas.draw()

    def onClickRelease(self, event):
        '''
        GUI: on click released event
        '''
        if self.dragging:
            self.points_spatial.remove(self.drag_start_coord)
            x, y = self.apply_step(event.xdata, event.ydata)
            self.picked_artist.center = (x, y)
            self.points_spatial.add((x, y))
            self.fig_spatial.canvas.draw()
        self.dragging = False

    def onkeyReleased(self, event):
        '''
        GUI: on key released event
        '''
        #print('you released', event.key, event.xdata, event.ydata)
        if event.key == 'control':
            self.control_pressed = False
        elif event.key == OPEN_KEY:
            # Load
            filename = self.open_file_dialog()
            if filename:
                self.clear_spatial()

                self.load_file(filename)
                self.ax_spatial.set_title('Spatial: {}'.format(os.path.basename(filename)))

                min_x, max_x, min_y, max_y = smos.get_min_max(self.points_spatial)

                self.ax_spatial.set_xlim(min_x-1, max_x+1)
                self.ax_spatial.set_ylim(min_y-1, max_y+1)

                self.ax_spatial.set_xticks(np.arange(min_x, max_x, 1))
                self.ax_spatial.set_yticks(np.arange(min_y, max_y, 1))

                self.fig_spatial.canvas.draw()

        elif event.key == SAVE_KEY:
            # Save
            f = self.save_file_dialog()
            if f:
                with f:
                    self.save_file(f)

    def onkeyPress(self, event):
        '''
        GUI: on key press event
        '''
        #print('you pressed', event.key, event.xdata, event.ydata)
        if event.key == 'control':
            self.control_pressed = True
        elif event.key == GENERATE_KEY:
            # Create freq figure if it doesn't exist
            if not plt.fignum_exists(2):
                self.create_freq_figure()

            self.ax_freq.set_title('Computing...')
            plt.ioff()

            self.generate_freq()

            mins_maxs = smos.get_min_max(self.points_freq)
            min_x, max_x, min_y, max_y = [smos.key2freq(v)*q/lamb for v in mins_maxs]

            self.ax_freq.set_xlim(min_x-1, max_x+1)
            self.ax_freq.set_ylim(min_y-1, max_y+1)

            self.ax_freq.set_title('Antennas Fourier')
            self.fig_freq.canvas.draw()
            plt.ion()

        elif event.key == 'x':
            if self.picked_artist in self.ax_spatial.artists:
                self.points_spatial.remove(self.picked_artist.center)
                self.ax_spatial.artists.remove(self.picked_artist)
                self.fig_spatial.canvas.draw()
        elif event.key == 'z':
            self.step = 0.25 if not self.step else None
        elif event.key == 'ctrl+z':
            # Remove last point
            if len(self.ax_spatial.artists) > 0:
                x, y = self.ax_spatial.artists[-1].center
                self.points_spatial.remove((x, y))
                del self.ax_spatial.artists[-1]
                self.fig_spatial.canvas.draw()


    def onClose(self, _):
        '''
        GUI: on figure closed
        '''
        # Close both of them
        plt.close(self.fig_freq)
        plt.close(self.fig_spatial)

# Create main class and start everything
antennas_spatial = AntennasSpatial()
