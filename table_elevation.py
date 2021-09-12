""" This module stores data for elevation offset (radians)
    for VLP16 lidar
"""

import numpy as np

filename = 'table_elevation.npy'

# degrees
elevation = np.array(
    [
        -15,
        1,
        -13,
        3,
        -11,
        5,
        -9,
        7,
        -7,
        9,
        -5,
        11,
        -3,
        13,
        -1,
        15
    ]
)

# convert to radians
elevation = np.deg2rad(elevation)

np.save(filename, elevation)
