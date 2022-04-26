from pathlib import Path
import importlib
import numpy as np
import sys

path_to_source = Path(__file__).parent / 'PhantomBuilder'
sys.path.insert(0, str(path_to_source))
importlib.invalidate_caches()  # maybe is not needed
import PhantomBuilder  # note the slightly clumsy import; we have to do it like this so FreeCAD finds the module
importlib.reload(PhantomBuilder)


'''
This demonstrates a script to build a multisclice phantom in FreeCAD.
This script MUST be called from FreeCAD, it will not run when called directly.
'''
Nslices = 9  # make this an odd number to make sure you have a slize at z=0
# the mean z position of the markers (defined by hole_depth) will define the Zposition
SliceZPositions = np.linspace(-140, 140, Nslices)

# Calculate which slice is closest to isocenter
CentralSliceZ = np.abs(SliceZPositions - 0).min()

# draw all the slices:
for i, z_pos in enumerate(SliceZPositions):

    if z_pos == CentralSliceZ:
        referenceRadius = 70
    else:
        referenceRadius = None

    Slice = PhantomBuilder.AddPhantomSlice(slice_shape='rectangle',
                                           slice_thickness=35, HVL_x=160, HVL_Y=160,
                                           hole_depth=17, hole_spacing=20,
                                           hole_radius=8.7 / 2,
                                           DSV=150, z_pos=-z_pos,
                                           LoadRegion={'shape': 'rectangle', 'width': 100, 'height': 200},
                                           ReferenceCrosshairRadius=referenceRadius,
                                           GuideRods={'radius': 5, 'position': 30, 'height': 370},
                                           HoleCentroids='ROI_polar')

    Slice.add_full_scale_drawing()

Slice.draw_DSV()
Slice.draw_Load()
Slice.draw_Guide()


