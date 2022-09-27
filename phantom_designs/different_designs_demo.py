from pathlib import Path
import importlib
import numpy as np
import sys

path_to_source = Path(__file__).parent.parent
sys.path.insert(0, str(path_to_source))
importlib.invalidate_caches()  # maybe is not needed
from PhantomDesign import PhantomBuilder
importlib.reload(PhantomBuilder)

"""
This script was set up to demonstrate some of the different phantom designs that can be generated with this code
"""
different_designs =['elipsoid_cartesian', 'small_rectangle_polar', 'eliptic_user_defined']
design_to_build = different_designs[1]
Nslices = 1  # just need one slice for demo
SliceZPositions = 0

if design_to_build == 'elipsoid_cartesian':
    Slice = PhantomBuilder.AddPhantomSlice(slice_shape='ellipse',
                                           slice_thickness=35, HVL_x=200, HVL_Y=160,
                                           hole_depth=17, hole_spacing=20,
                                           hole_radius=8.7 / 2,
                                           z_pos=-SliceZPositions,
                                           GuideRods={'radius': 5, 'position': 30, 'height': 370},
                                           HoleCentroids='cartesian',
                                           DSV=None,
                                           bottom_cut=50)
    Slice.add_full_scale_drawing()

elif design_to_build == 'small_rectangle_polar':
    Slice = PhantomBuilder.AddPhantomSlice(slice_shape='rectangle',
                                           slice_thickness=20, HVL_x=100, HVL_Y=100,
                                           hole_depth=17, hole_spacing=20,
                                           hole_radius=5,
                                           z_pos=-SliceZPositions,
                                           HoleCentroids='ROI_polar',
                                           DSV=50,
                                           bottom_cut=0)
    Slice.add_full_scale_drawing()

elif design_to_build == 'eliptic_user_defined':



    Slice = PhantomBuilder.AddPhantomSlice(slice_shape='ellipse',
                                           slice_thickness=35, HVL_x=200, HVL_Y=160,
                                           hole_depth=17, hole_spacing=20,
                                           hole_radius=8.7 / 2,
                                           z_pos=-SliceZPositions,
                                           GuideRods={'radius': 5, 'position': 30, 'height': 370},
                                           HoleCentroids='cartesian',
                                           DSV=None,
                                           bottom_cut=50)
    Slice.add_full_scale_drawing()


