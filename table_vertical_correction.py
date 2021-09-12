""" This module stores data for vertical correction (metres)
    for VLP16 lidar
"""

import numpy as np

filename = 'table_vertical_correction.npy'

# millimetres
vertical_correction = np.array(
    [
        11.2,
        -0.7,
        9.7,
        -2.2,
        8.1,
        -3.7,
        6.6,
        -5.1,
        5.1,
        -6.6,
        3.7,
        -8.1,
        2.2,
        -9.7,
        0.7,
        -11.2
    ]
)

# convert to millimetres
vertical_correction = vertical_correction / 1000

np.save(filename, vertical_correction)
