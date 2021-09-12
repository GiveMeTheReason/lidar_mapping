""" This script transforms data package from lidar
    to a list containing point cloud
"""

import numpy as np
#import matplotlib.pyplot as plt


def get_header(db):
    return db[0:84]


def get_flag(db):
    flag = np.empty(12, dtype=object)
    pos = 84
    for i in range(12):
        flag[i] = db[pos:pos+4]
        pos += 200
    return flag


def get_azimuth(db):
    azimuth = np.zeros(12, float)
    pos = 88
    for i in range(12):
        azimuth[i] = int(db[pos+2:pos+4] + db[pos:pos+2], 16)/100
        pos += 200
    return np.deg2rad(azimuth)


def get_points_radius(db):
    points_radius = np.zeros((24, 16), float)
    pos = 92
    for i in range(24):
        for j in range(16):
            points_radius[i][j] = int(db[pos+2:pos+4] + db[pos:pos+2], 16)*2/1000
            pos += 6
        if i % 2:
            pos += 6
    return points_radius


def get_points_reflectivity(db):
    points_reflectivity = np.zeros((24, 16), int)
    pos = 92
    for i in range(24):
        for j in range(16):
            points_reflectivity[i][j] = int(db[pos+4:pos+6], 16)
            pos += 6
        if i % 2:
            pos += 6
    return points_reflectivity


def get_timestamp(db):
    return db[2484:2492]


def get_factory_bytes(db):
    return db[2492:2496]


'''
def get_points_radius_and_reflectivity(db):
    points_radius_and_reflectivity = np.zeros((24, 16, 2), float)
    pos = 92
    for i in range(24):
        for j in range(16):
            points_radius_and_reflectivity[i][j][0] = int(db[pos+2:pos+4] + db[pos:pos+2], 16)*2/1000
            points_radius_and_reflectivity[i][j][1] = int(db[pos+4:pos+6], 16)
            pos += 6
        if i % 2:
            pos += 6
    return points_radius_and_reflectivity


def filter_structered_points(points_radius_and_reflectivity, threshold=0.5):
    filtered_points = points_radius_and_reflectivity
    for i in range(24):
        m = np.zeros(0)
        for j in range(16):
            if filtered_points[i][j][0] and filtered_points[i][j][1]:
                m = np.append(m, filtered_points[i][j][0])
        m.sort()
        if len(m):
            d = np.zeros(len(m))
            for k in range(1, len(d)):
                d[k] = m[k] - m[k-1]
            d[0] = 100
            d = np.append(d, 100)
            for k in range(len(d)-1):
                if (d[k] >= threshold) and (d[k+1] >= threshold):
                    for j in range(16):
                        if filtered_points[i][j][0] == m[k]:
                            filtered_points[i][j][0] = 0
                            break
    return filtered_points


def get_1(points_radius_and_reflectivity, azimuth, azimuth_offset, elevation, vertical_correction):
    points = np.zeros((0, 4), float)
    for i, cycle in enumerate(points_radius_and_reflectivity):
        for j, point in enumerate(cycle):
            if (rad_min <= point[0] <= rad_max) and (refl_min <= point[1] <= refl_max):
                item = np.zeros((1, 4))
                item[0, 0] = point[0] * np.cos(elevation[j]) * np.sin(azimuth[i%2]+azimuth_offset[i%2][j])
                item[0, 1] = point[0] * np.cos(elevation[j]) * np.cos(azimuth[i%2]+azimuth_offset[i%2][j])
                item[0, 2] = point[0] * np.sin(elevation[j]) + vertical_correction[j]
                item[0, 3] = point[1]
                points = np.concatenate((points, item))
    return points
'''

'''
def get_points(points_radius, azimuth, azimuth_offset, elevation, vertical_correction):
    points = np.zeros((24*16, 3), float)
    for i in range(24):
        for j in range(16):
            if (rad_min <= points_radius[i][j] <= rad_max):
                points[i*16+j, 0] = points_radius[i][j] * np.cos(elevation[j]) * np.sin(azimuth[i%2]+azimuth_offset[i%2][j])
                points[i*16+j, 1] = points_radius[i][j] * np.cos(elevation[j]) * np.cos(azimuth[i%2]+azimuth_offset[i%2][j])
                points[i*16+j, 2] = points_radius[i][j] * np.sin(elevation[j]) + vertical_correction[j]
            else:
                points[i*16+j] = [0, 0, 0]
    return points


def filter_zero_points(points):
    filtered_points = np.zeros((0, 3), float)
    for item in points:
        if not item.all() == 0:
            filtered_points = np.concatenate((filtered_points, item.reshape(1, 3)))
    return filtered_points
'''

def descriptor(db):
    '''
    Returns a list (Nx4) of points (float) [distance, intensity, azimuth, laser_id]
    '''
    # Filter stuff
    rad_min = 0.01
    rad_max = 50
    refl_min = 1
    refl_max = 100

    points = np.zeros((0, 4), float)
    point = np.zeros((1, 4), float)
    db_lenght = 2496
    pos = 0
    while True:
        add = db[pos:].find('ffee')
        if add >= 0:
            pos += add + 4
        else:
            break
        next_add = db[pos:].find('ffee')
        if (next_add == 196) or (next_add == -1 and pos == 2288):
            pass
        else:
            pos += next_add
            if next_add == -1:
                pos = 2496
            continue
        azimuth = np.deg2rad(int(db[pos+2:pos+4] + db[pos:pos+2], 16)/100)
        if azimuth > 2*np.pi:
            continue
        pos += 4
        for i in range(32):
            dist = int(db[pos+2:pos+4] + db[pos:pos+2], 16)*2/1000
            intensity = int(db[pos+4:pos+6], 16)
            if (rad_min <= dist <= rad_max) and (refl_min <= intensity <= refl_max):
                point[0][0] = dist
                point[0][1] = intensity
                point[0][2] = azimuth
                point[0][3] = i
                points = np.concatenate((points, point))
            pos += 6
    return points


def get_desc(points_desc, azimuth_offset, elevation, vertical_correction):
    '''
    Returns a list of points (float) [x, y, z, intensity]
    '''
    points = np.zeros(points_desc.shape, float)
    for i in range(points_desc.shape[0]):
        azimuth = points_desc[i][2]
        j = int(points_desc[i][3])
        points[i][0] = points_desc[i][0] * np.cos(elevation[j%16]) * np.sin(azimuth+azimuth_offset[j//16][j%16])
        points[i][1] = points_desc[i][0] * np.cos(elevation[j%16]) * np.cos(azimuth+azimuth_offset[j//16][j%16])
        points[i][2] = points_desc[i][0] * np.sin(elevation[j%16]) + vertical_correction[j%16]
        points[i][3] = points_desc[i][1]
    return points


def get_scan(cycle, h):
    db_lenght = 2496
    azimuth_offset = np.load('table_azimuth_10Hz.npy')
    elevation = np.load('table_elevation.npy')
    vertical_correction = np.load('table_vertical_correction.npy')
    points = np.zeros((0, 4), float)
    for i in range(len(cycle)):
        db = h[cycle[i]:cycle[i]+db_lenght]
        points_1 = get_desc(descriptor(db), azimuth_offset, elevation, vertical_correction)
        points = np.concatenate((points, points_1))
    return points


#now = datetime.now()
#print(datetime.now()-now)
'''
h = open('2014-11-10-10-36-54_Velodyne-VLP_10Hz-County Fair.pcap', 'rb').read().hex()
azimuth_offset = np.load('table_azimuth_10Hz.npy')
elevation = np.load('table_elevation.npy')
vertical_correction = np.load('table_vertical_correction.npy')

db_lenght = 2496

# Test data
prot_1 = [80, 2608, 5136, 8804, 11332, 13860, 16388, 18916, 21444, 23972, 26500,
        29028, 31556, 34084, 37752, 40280, 42808, 45336, 47864, 51532, 54060,
        57728, 60256, 62784, 65312, 67840, 70368, 72896, 75424, 79092, 81620,
        84148, 86676, 89204, 91732, 95400, 99068, 101596, 104124, 106652, 109180,
        111708, 114236, 116764, 120432, 122960, 125488, 128016, 130544, 133072,
        135600, 139268, 142936, 145464, 147992, 150520, 153048, 155576, 158104,
        161772, 164300, 166828, 169356, 171884, 174412, 176940, 180608, 184276,
        186804, 189332, 191860, 194388, 196916, 199444, 203112]

prot_2 = [205640, 208168, 210696, 213224, 215752, 218280, 221948, 224476, 228144,
        230672, 233200, 235728, 238256, 240784, 244452, 246980, 249508, 252036,
        254564, 257092, 259620, 263288, 265816, 268344, 272012, 274540, 277068,
        279596, 282124, 285792, 288320, 290848, 293376, 295904, 298432, 300960,
        303488, 307156, 309684, 312212, 315880, 318408, 320936, 323464, 327132,
        329660, 332188, 334716, 337244, 339772, 342300, 344828, 348496, 351024,
        353552, 356080, 359748, 362276, 364804, 368472, 371000, 373528, 376056,
        378584, 381112, 383640, 386168, 389836, 392364, 394892, 397420, 399948,
        403616, 406144, 409812]

prot_3 = [202000048, 202002576, 202005104, 202007632, 202010160, 202012688, 202015216,
        202018884, 202022552, 202025080, 202027608, 202030136, 202032664, 202035192,
        202037720, 202041388, 202043916, 202046444, 202048972, 202051500, 202054028,
        202056556, 202059084, 202062752, 202065280, 202067808, 202070336, 202072864,
        202075392, 202077920, 202081588, 202084116, 202086644, 202089172, 202091700,
        202094228, 202096756, 202099284, 202102952, 202106620, 202109148, 202111676,
        202114204, 202116732, 202119260, 202121788, 202125456, 202127984, 202130512,
        202133040, 202135568, 202138096, 202140624, 202144292, 202146820, 202150488,
        202153016, 202155544, 202158072, 202160600, 202164268, 202166796, 202169324,
        202171852, 202174380, 202176908, 202179436, 202181964, 202185632, 202188160,
        202190688, 202194356, 202196884, 202199412, 202201940]

prot_4 = [202205608, 202208136, 202210664, 202213192, 202215720, 202218248, 202220776,
        202223304, 202226972, 202229500, 202232028, 202234556, 202238224, 202240752,
        202243280, 202245808, 202249476, 202252004, 202254532, 202257060, 202259588,
        202262116, 202264644, 202268312, 202270840, 202273368, 202275896, 202278424,
        202282092, 202284620, 202287148, 202290816, 202293344, 202295872, 202298400,
        202300928, 202303456, 202305984, 202309652, 202312180, 202314708, 202317236,
        202319764, 202322292, 202325960, 202328488, 202332156, 202334684, 202337212,
        202339740, 202342268, 202344796, 202347324, 202350992, 202353520, 202356048,
        202358576, 202361104, 202363632, 202366160, 202369828, 202373496, 202376024,
        202378552, 202381080, 202383608, 202386136, 202388664, 202392332, 202394860,
        202397388, 202399916, 202402444, 202404972, 202407500]

prot_5 = [404002196, 404004724, 404007252, 404009780, 404012308, 404014836, 404017364,
        404021032, 404023560, 404026088, 404028616, 404031144, 404033672, 404036200,
        404038728, 404041256, 404044924, 404047452, 404049980, 404052508, 404055036,
        404057564, 404061232, 404063760, 404066288, 404068816, 404071344, 404073872,
        404076400, 404080068, 404082596, 404085124, 404088792, 404091320, 404093848,
        404096376, 404098904, 404102572, 404105100, 404107628, 404110156, 404112684,
        404115212, 404117740, 404120268, 404123936, 404126464, 404128992, 404132660,
        404135188, 404137716, 404140244, 404143912, 404146440, 404148968, 404151496,
        404154024, 404156552, 404159080, 404161608, 404165276, 404167804, 404170332,
        404172860, 404176528, 404179056, 404181584, 404185252, 404187780, 404190308,
        404192836, 404195364, 404197892, 404200420, 404202948]
'''

'''
# Filter stuff
refl_min = 1
refl_max = 100
rad_min = 1
rad_max = 20
threshold = 1000
'''

'''
points = np.zeros((0, 3), float)
for i in range(len(prot)):
    db = h[prot[i]:prot[i]+db_lenght]
    points_1 = filter_zero_points(get_points(get_points_radius(db), get_azimuth(db), azimuth_offset, elevation, vertical_correction))
    points = np.concatenate((points, points_1))
print(points.shape)
'''
'''
points = np.zeros((0, 4), float)
for i in range(len(prot)):
    db = h[prot[i]:prot[i]+db_lenght]
    points_1 = get_1(filter_structered_points(get_points_radius_and_reflectivity(db), threshold), get_azimuth(db), azimuth_offset, elevation, vertical_correction)
    points = np.concatenate((points, points_1))
print(points.shape)
'''

'''
# Tests
prot = prot_3
points = np.zeros((0, 4), float)
for i in range(len(prot)):
    db = h[prot[i]:prot[i]+db_lenght]
    points_1 = get_desc(descriptor(db), azimuth_offset, elevation, vertical_correction)
    points = np.concatenate((points, points_1))

points = get_scan(prot_3)
print(points.shape)

#print(datetime.now()-now)

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.scatter(points[:,0], points[:,1], points[:,2], s=1, c=points[:,3], marker='o') # c='#0000ff'
plt.show()
'''
