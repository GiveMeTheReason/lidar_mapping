""" This module stores data for azimuth offset (radians)
    for VLP16 lidar
"""

import numpy as np

filename = 'table_azimuth_10Hz.npy'
hz = 10
angle_speed = hz*360
cycle_time = 55.296*10**-6
between_firings = 2.304*10**-6
recharge_time = 18.432*10**-6

azimuth_offset = np.zeros((2, 16))
time = 0
for i in range(2):
    for j in range(16):
        azimuth_offset[i][j] = angle_speed*time
        time += between_firings
    time += recharge_time

azimuth_offset = np.deg2rad(azimuth_offset)

np.save(filename, azimuth_offset)
