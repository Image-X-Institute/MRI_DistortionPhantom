from pathlib import Path
import importlib
import numpy as np
import sys
path_to_source = Path(__file__).parent.parent
sys.path.insert(0, str(path_to_source))
importlib.invalidate_caches()  # maybe is not needed
from PhantomDesign import PhantomBuilder

importlib.reload(PhantomBuilder)

'''
This is the script which I used to generate a design which was sent to Evolution Gear
'''
Nslices = 11 # make this an odd number to make sure you have a slize at z=0
SliceZPositions = np.linspace(-150, 150, Nslices)
SliceThickness = np.mean(np.abs(np.diff(SliceZPositions)))

for i, z_pos in enumerate(SliceZPositions):
    # setup load:
    if not int(z_pos) == 0 and (abs(z_pos) < 120):
        '''
        vasline size:
        - 8 cm depth: three slices 
        - 10 cm wide
        - 10.5 cm high
        '''
        load = {'shape': 'rectangle', 'width': 110, 'height': 510}
    else:
        load = None
    # set up crosshair
    if int(z_pos) == 0:
        print(f'z_pos={z_pos}; dong!')
        referenceRadius = 70
    else:
        referenceRadius = None
    # set up end slices:
    if abs(int(z_pos)) == 150:
        HoleStart = 0
    else:
        HoleStart = None

    Slice = PhantomBuilder.AddPhantomSlice(slice_shape='rectangle',
                                           slice_thickness=SliceThickness, HVL_x=390 / 2, HVL_Y=390 / 2,
                                           hole_depth=15, hole_spacing=25,
                                           hole_radius=8.7 / 2,
                                           DSV=150, z_pos=z_pos,
                                           LoadRegion=load,
                                           GuideRods={'radius': 5, 'position': 20, 'height': 370},
                                           HoleCentroids='ROI_polar',
                                           ReferenceCrosshairRadius=referenceRadius,
                                           bottom_cut=30,
                                           hole_start=HoleStart)
    Slice.add_full_scale_drawing()

    z_array = np.ones(np.shape(Slice.HoleCentroids)[1]) * z_pos
    marker_positions_temp = np.vstack([np.array(Slice.HoleCentroids), z_array])
    try:
        marker_positions = np.hstack([marker_positions, marker_positions_temp])
    except NameError:
        marker_positions = marker_positions_temp


Slice.draw_DSV()
Slice.draw_Guide()

marker_positions = np.array(marker_positions)
np.savetxt(r'C:\Users\Brendan\Documents\python\MRI_DistortionPhantom\marker_positions.txt', marker_positions)


"""
- adjusted hole size
- enlarged DSV to 160
- extended phantom length - will guide rods be long enough?
- added large load regions for vaseline either side of central slice
- saved all marker positions to a text file
"""