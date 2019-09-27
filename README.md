# antennas_simul
Interferometric Antennas Interactive Toy

Author: Miguel Colom
Website: http://mcolom.info

This is a simple Python3 program that allows to quickly design the spatial position of the antennas of an interferometric instrument (say, SMOS) and view the corresponding sampling in Fourier, with the associated multiplicities.
It read/saves the position of the antennas in the instrument from text files. Each line must contain the X and Y coordinates of the antenna in meters, separated by a comma.

Keys:
d: open a file
a: save current configuration to a file
ENTER: compute and visualize the Fourier sampling, along with the multiplicity of each visibility.
You can change these keys by editing the antennas.py file, if you wish.

Move the antennas by dragging them with the mouse. To add more, click on the window while pressing the Ctrl key.

The program assumes that the units in the spatial plane are meters, and that the geometry is Cartesian. Therefore the sampling frequencies will at (a1 - a2) * q / lambda, with a1, a2 the position of the antennas, lambda = 299792458 / 1413e6 = 0.21 and q=2. If you assume SMOS-HR or any other configuration with a Cartesian geometry, this is correct. If you are instead simulating the existing SMOS (hexagonal geometry), change q to sqrt(3) in the source code.

To install it:
- Linux users: just unzip the file, chmod +x antennas.py and run it.
- Windows users: you need to install a Python 3 environment in your machine. It should work. I've seen it working on Linux, Windows, and Mac OS.

All users: most probably you'll need to install a few packages at user level with pip3 (matplotlib, numpy, ...) or OS level (python3-tk, ...)
