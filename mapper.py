'''
# mapper v1
import numpy as np
import matplotlib.pyplot as plt
import icp
import vlp16_reader

cloud = np.zeros((0, 3))
T = np.eye(4)

h = open('2014-11-10-10-36-54_Velodyne-VLP_10Hz-County Fair.pcap', 'rb').read().hex()

# data_prot 42 bytes
data_prot = 'ff ff ff ff ff ff 60 76 88 00 00 00 08 00 45 00\
            04 d2 00 00 40 00 ff 11 b4 aa c0 a8 01 c8 ff ff\
            ff ff 09 40 09 40 04 be 00 00'.replace(' ', '')

# Return data from one rotation (75 data blocks for 10 Hz)
# differense between data blocks: 2528 or 3668 symbols
cycle = [0]*75
counter = 0
pos = 103241000 # 40981200 + h[40981200:].find(data_prot)
while counter < 75:
    cycle[counter] = pos
    counter += 1
    if h[pos+2528:pos+2528+84] == data_prot:
        pos += 2528
    elif h[pos+3668:pos+3668+84] == data_prot:
        pos += 3668
    elif h[pos+4808:pos+4808+84] == data_prot:
        pos += 4808
    elif h[pos+5948:pos+5948+84] == data_prot:
        pos += 5948
    else:
        nxt = h[pos+1:].find(data_prot)
        print("ALERT!", nxt+1)
        if nxt == -1:
            cycle[counter:] = [pos]*(75-counter)
            break
        else:
            pos += nxt + 1

points = vlp16_reader.get_scan(cycle, h)
points = points[:, 0:3]
points = points[points[:,2] > -1.3]
cloud = np.concatenate((cloud, points))

# --------------------------------------------------

print(0, cloud.shape[0], pos)
i = 0
ilim = 2000
while i < ilim:
    cycle = [0]*75
    counter = 0
    while counter < 75:
        cycle[counter] = pos
        counter += 1
        if h[pos+2528:pos+2528+84] == data_prot:
            pos += 2528
        elif h[pos+3668:pos+3668+84] == data_prot:
            pos += 3668
        elif h[pos+4808:pos+4808+84] == data_prot:
            pos += 4808
        elif h[pos+5948:pos+5948+84] == data_prot:
            pos += 5948
        else:
            nxt = h[pos+1:].find(data_prot)
            print("ALERT!", nxt+1)
            if nxt == -1:
                cycle[counter:] = [pos]*(75-counter)
                i = ilim
                break
            else:
                pos += nxt + 1

    if (i+1) % 5 == 0:
        points = vlp16_reader.get_scan(cycle, h)
        points = points[:, 0:3]
        points = points[points[:,2] > -1.3]

        T, distances, iterations = icp.icp(points, cloud, init_pose=T, tolerance=0.000001)
        points = np.dot(T[0:3,0:3], points.T).T
        points += T[0:3, 3]
        for j in range(len(distances)):
            if 1.5 < distances[j] < 3:
                cloud = np.concatenate((cloud, points[j].reshape(1, 3)))
        print(i+1, cloud.shape[0], pos)
    i += 1

print(T)
# --------------------------------------------------

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.scatter(cloud[:,0], cloud[:,1], cloud[:,2], s=1, c='#0000ff', marker='o') # c='#0000ff'
plt.show()
'''
'''
# mapper v2
import numpy as np
import matplotlib.pyplot as plt
import icp
import vlp16_reader

cloud = np.zeros((0, 4))
T = np.eye(4)

h = open('2014-11-10-10-36-54_Velodyne-VLP_10Hz-County Fair.pcap', 'rb').read().hex()

# data_prot 42 bytes
data_prot = 'ff ff ff ff ff ff 60 76 88 00 00 00 08 00 45 00\
            04 d2 00 00 40 00 ff 11 b4 aa c0 a8 01 c8 ff ff\
            ff ff 09 40 09 40 04 be 00 00'.replace(' ', '')

# Return data from one rotation (75 data blocks for 10 Hz)
# differense between data blocks: 2528 or 3668 symbols
cycle = [0]*75
counter = 0
pos = 20603960 # 20603960 (100 frame) 41211260 (200 frame)
while counter < 75:
    cycle[counter] = pos
    counter += 1
    if h[pos+2528:pos+2528+84] == data_prot:
        pos += 2528
    elif h[pos+3668:pos+3668+84] == data_prot:
        pos += 3668
    elif h[pos+4808:pos+4808+84] == data_prot:
        pos += 4808
    elif h[pos+5948:pos+5948+84] == data_prot:
        pos += 5948
    else:
        nxt = h[pos+1:].find(data_prot)
        print("ALERT!", nxt+1)
        if nxt == -1:
            cycle[counter:] = [pos]*(75-counter)
            break
        else:
            pos += nxt + 1

cur_points = vlp16_reader.get_scan(cycle, h)
cur_points[:,3] = 1
cur_points = cur_points[cur_points[:,2] > -1.3]
cloud = np.concatenate((cloud, cur_points))
col = np.zeros((cloud.shape[0], 1)).reshape(cloud.shape[0])

# --------------------------------------------------

print(0, cloud.shape[0], pos)
i = 0
ilim = 100
T_new = np.eye(4)
while i < ilim:
    cycle = [0]*75
    counter = 0
    while counter < 75:
        cycle[counter] = pos
        counter += 1
        if h[pos+2528:pos+2528+84] == data_prot:
            pos += 2528
        elif h[pos+3668:pos+3668+84] == data_prot:
            pos += 3668
        elif h[pos+4808:pos+4808+84] == data_prot:
            pos += 4808
        elif h[pos+5948:pos+5948+84] == data_prot:
            pos += 5948
        else:
            nxt = h[pos+1:].find(data_prot)
            print("ALERT!", nxt+1)
            if nxt == -1:
                cycle[counter:] = [pos]*(75-counter)
                i = ilim
                break
            else:
                pos += nxt + 1

    prev_points = np.copy(cur_points)
    cur_points = vlp16_reader.get_scan(cycle, h)
    cur_points[:,3] = 1
    cur_points = cur_points[cur_points[:,2] > -1.3]

    T_prev = np.copy(T_new)
    T_new, distances, iterations = icp.icp(cur_points, prev_points, init_pose=T_prev, max_iterations=10, tolerance=0.00001)
    T = np.dot(T, T_new)
    add_points = np.dot(T, cur_points.T).T
    cloud = np.concatenate((cloud, add_points[distances[:] > 1.5]))
    #cloud = np.concatenate((cloud, add_points))
    print(i+1, cloud.shape[0], pos)
    i += 1
    col = np.concatenate((col, i*np.ones((cloud.shape[0]-col.shape[0], 1)).reshape(cloud.shape[0]-col.shape[0])))

print(T)
# --------------------------------------------------

#col = np.ones((cloud.shape[0], 1)).reshape(cloud.shape[0])
#col[:first] = 0
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.scatter(cloud[:,0], cloud[:,1], cloud[:,2], s=1, c=col, marker='o') # c='#0000ff'
plt.show()
'''

# mapper v3
import numpy as np
import matplotlib.pyplot as plt
import icp
import vlp16_reader
from datetime import datetime


now = datetime.now()

cloud = np.zeros((0, 4))
T = np.eye(4)

h = open('2014-11-10-10-36-54_Velodyne-VLP_10Hz-County Fair.pcap', 'rb').read().hex()

# data_prot 42 bytes
data_prot = 'ff ff ff ff ff ff 60 76 88 00 00 00 08 00 45 00\
            04 d2 00 00 40 00 ff 11 b4 aa c0 a8 01 c8 ff ff\
            ff ff 09 40 09 40 04 be 00 00'.replace(' ', '')

# Return data from one rotation (75 data blocks for 10 Hz)
# differense between data blocks: 2528 or 3668 symbols
cycle = [0]*75
counter = 0
pos = 0 # 20603960 (100 frame) 41211260 (200 frame)
while counter < 75:
    cycle[counter] = pos
    counter += 1
    if h[pos+2528:pos+2528+84] == data_prot:
        pos += 2528
    elif h[pos+3668:pos+3668+84] == data_prot:
        pos += 3668
    elif h[pos+4808:pos+4808+84] == data_prot:
        pos += 4808
    elif h[pos+5948:pos+5948+84] == data_prot:
        pos += 5948
    else:
        nxt = h[pos+1:].find(data_prot)
        print("ALERT!", nxt+1)
        if nxt == -1:
            cycle[counter:] = [pos]*(75-counter)
            break
        else:
            pos += nxt + 1

cur_points = vlp16_reader.get_scan(cycle, h)
cur_points[:,3] = 1
cur_points = cur_points[cur_points[:,2] > -1.3]
cloud = np.concatenate((cloud, cur_points))
#col = np.zeros((cloud.shape[0], 1)).reshape(cloud.shape[0])

# --------------------------------------------------

print(0, cloud.shape[0], pos)
i = 0
ilim = 300
while i < ilim:
    cycle = [0]*75
    counter = 0
    while counter < 75:
        cycle[counter] = pos
        counter += 1
        if h[pos+2528:pos+2528+84] == data_prot:
            pos += 2528
        elif h[pos+3668:pos+3668+84] == data_prot:
            pos += 3668
        elif h[pos+4808:pos+4808+84] == data_prot:
            pos += 4808
        elif h[pos+5948:pos+5948+84] == data_prot:
            pos += 5948
        else:
            nxt = h[pos+1:].find(data_prot)
            print("ALERT!", nxt+1)
            if nxt == -1:
                cycle[counter:] = [pos]*(75-counter)
                i = ilim
                break
            else:
                pos += nxt + 1

    prev_points = np.copy(cur_points)
    cur_points = vlp16_reader.get_scan(cycle, h)
    cur_points[:,3] = 1
    cur_points = cur_points[cur_points[:,2] > -1.3]

    T_new2, distances, iterations = icp.icp(cur_points[:,:2], prev_points[:,:2], max_iterations=10, tolerance=0.001)
    T_new = np.eye(4)
    T_new[0:2,0:2] = T_new2[0:2,0:2]
    T_new[0:2,3] = T_new2[0:2,2]
    T = np.dot(T, T_new)
    add_points = np.dot(T, cur_points.T).T
    cloud = np.concatenate((cloud, add_points[distances[:] > 0.5]))
    #cloud = np.concatenate((cloud, add_points))
    print(i+1, cloud.shape[0], pos)
    i += 1
    #col = np.concatenate((col, i*np.ones((cloud.shape[0]-col.shape[0], 1)).reshape(cloud.shape[0]-col.shape[0])))

print(T)
# --------------------------------------------------

print(datetime.now()-now)

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.scatter(cloud[:,0], cloud[:,1], cloud[:,2], s=1, c='#0000ff', marker='o') # c='#0000ff'
plt.show()
