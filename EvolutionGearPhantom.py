from pathlib import Path
import importlib
import numpy as np
import sys


path_to_source = Path(__file__).parent
sys.path.insert(0, str(path_to_source))
importlib.invalidate_caches()  # maybe is not needed
for path in sys.path:
    print(path)

import PhantomBuilder  # note the slightly clumsy import; we have to do it like this so FreeCAD finds the module
importlib.reload(PhantomBuilder)

'''
This is the script which I used to generate a design which was sent to Evolution Gear
'''
Nslices = 11 # make this an odd number to make sure you have a slize at z=0
SliceZPositions = np.linspace(-150, 150, Nslices)

for i, z_pos in enumerate(SliceZPositions):
    if abs(z_pos) < 90 and (not z_pos == 0):
        load = {'shape': 'rectangle', 'width': 70, 'height': 200}
    else:
        load = None

    Slice = PhantomBuilder.AddPhantomSlice(slice_shape='rectangle',
                                           slice_thickness=30, HVL_x=390 / 2, HVL_Y=390 / 2,
                                           hole_depth=15, hole_spacing=25,
                                           hole_radius=8.7 / 2,
                                           DSV=180, z_pos=z_pos,
                                           LoadRegion=load,
                                           GuideRods={'radius': 5, 'position': 20, 'height': 370},
                                           HoleCentroids='ROI_polar')

    z_array = np.ones(np.shape(Slice.HoleCentroids)[1]) * z_pos
    marker_positions_temp = np.array(Slice.HoleCentroids) + z_array
    print(f'shape of XT = {np.shape(Slice.HoleCentroids)}; shape of z = {np.shape(z_array)}; shape of marker positions = {np.shape(marker_positions_temp)}')
    # try:
    #     marker_positions = np.stack([marker_positions, marker_positions_temp])
    # except NameError:
    #     marker_positions = marker_positions_temp

Slice.draw_DSV()
Slice.draw_Guide()

# marker_positions = np.array(marker_positions)
# np.savetxt(r'C:\Users\Brendan\Documents\python\MRI_DistortionPhantom\PhantomBuilder.py', marker_positions)
# print(marker_positions)



print(f'N DSV markers: {Slice._n_markers_on_dsv}')

"""
- adjusted hole size
- enlarged DSV to 160
- extended phantom length to 165
"""