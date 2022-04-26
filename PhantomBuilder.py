# -*- coding: utf-8 -*-

import Draft  # note when this is run through FreeCAD, these libraries will already be available
import numpy as np
from pathlib import Path
import FreeCAD
import sys


# get the doc object (will happen every time this module gets called)
doc = FreeCAD.newDocument('DistPhantom')  # instantiate doc object

class AddPhantomSlice:
    """
    Draws a single slice of the phantom
    All dimensions in mm
    All inputs are optional; calling without defining will just use default value.

    :param slice_shape: Shape of base slice. Currently can only be 'rectangle' but others could be added.
    :type slice_shape: string
    :param slice_thickness: Thickness of slice in Z
    :type slice_thickness: float
    :param HVL_x: Half value of slice in X (Left/Right). For elipse this is equivalent to major radius
    :type HVL_x: float
    :param HVL_Y: Half value of slice in Y (Up/Down). For elipse this is equivalent to major radius
    :type HVL_Y: float
    :param hole_depth: Depth of holes. If value is > slice_thickness will cut completely through
    :type hole_depth: float
    :param hole_spacing: distance between hole centroids - only approximate, as there are integers involved!
    :type hole_spacing: float
    :param hole_radius: Radius of holes
    :type hole_radius: float
    :param hole_start: x/y coordinate to start holes at. Default is None, which will try and choose a sensible value.
    :type hole_start: None or float
    :param hole_stop: x/y coordinate to stop holes at. Default is None, which will try and choose a sensible value.
    :type hole_stop: None or float
    :param GridOffset: move the entire hole distrubution by this much. Allows for offset distributions in differenct
        slices
    :type GridOffset: float
    :param HoleCentroids: 'cartesian' or 'ROI_polar' will produce either cartesian or polar grids based on hole_spacing.
        User can instead specify the location of all hole centroids as a 2D list of X/Y points
        e.g. [[x1,x2,x3],[y1,y2,y3]]. The value of GridOffset will be applied to these points. If user values are entered,
        hole_stop and hole_start are ignored.
    :type HoleCentroids: string ('cartesian' or 'ROI_polar') or 2D list/numpy array
    :param z_pos: z position of the middle of the hole cutout.
    :type z_pos: float
    :param DSV: Circles representing this raddi at a given z value will be etched on each slice; if you choose ROI_polar
        for marker positions, the code will attempt to ensure good coverage over the DSV surface`
    :type DSV: None or float
    :param LoadRegion: Can specify a cylindrical or spherical load region which will be cut away
        geom each slice, e.g.
        | LoadRegion = {'shape': 'cylinder', 'radius': 100, 'height': 200} or,
        | LoadRegion = {'shape': 'sphere', 'radius': 100} (this is not well tested), or
        | LoadRegion={'shape': 'rectangle', 'width': 70, 'height': 200}, or
        | LoadRegion = None (default)
        | You can can also optionally add a key z_offset to move the load position along the z axis
    :type LoadRegion: None or Dict
    :param GuideRods: Adds one guide rod in each corner. Position is distance from edge.
        GuideRods = {'radius': 10, 'position': 20,'length': 350}
        See: https://www.essentracomponents.com/en-au/p/fully-threaded-studs-rods/0060110000vr
    :type GuideRods: None or Dict
    """

    def __init__(self, slice_shape='rectangle', slice_thickness=30, HVL_x=250, HVL_Y=250, z_pos=0, hole_depth=17,
                 hole_spacing=25,
                 hole_radius=8.7 / 2, hole_stop=None, GridOffset=0, HoleCentroids='cartesian', DSV=150,
                 LoadRegion=None,
                 ReferenceCrosshairRadius = None,
                 GuideRods=None,
                 hole_start=None):

        self.DSV = DSV
        self.slice_shape = slice_shape
        self.TableOffset = 100  # how far below iso the the table surface?
        self.HVL_x = HVL_x
        self.HVL_Y = HVL_Y
        self.z_pos = z_pos
        self.elipse_cutoff = self.HVL_Y - self.TableOffset  # this is the correct cut off so the center of the elipse is at isoceneter
        self.hole_spacing = hole_spacing
        self.hole_depth = hole_depth
        self.hole_radius = hole_radius
        self.LoadRegion = LoadRegion
        self.ReferenceCrosshairRadius = ReferenceCrosshairRadius
        self._n_markers_on_dsv = None
        self._n_markers = 0
        if hole_stop is None:
            self._calculate_hole_stop()
        else:
            self.hole_stop = hole_stop
        if hole_start is None:
            self._calculate_hole_start()
        else:
            self.hole_start = hole_start
        self.slice_thickness = slice_thickness
        self.GridOffset = GridOffset
        self.HoleCentroids = HoleCentroids
        
        self.GuideRods = GuideRods
        
        if self.DSV:  # nb none evaluates to false
            # calculate the intersection of the DSV with this slice location.
            self._roi_on_surface = self.DSV - abs(self.z_pos - self.hole_depth / 2)
            self._roi_on_marker_center = self.DSV - abs(self.z_pos)
            self._roi_radius_surface = np.sqrt((2 * self._roi_on_surface * self.DSV) - (self._roi_on_surface ** 2))
            self._roi_radius_center = np.sqrt(
                (2 * self._roi_on_marker_center * self.DSV) - (self._roi_on_marker_center ** 2))


        if HoleCentroids == 'ROI_polar':
            self._generate_roi_polar_hole_positions()
        elif HoleCentroids == 'cartesian':
            self._generate_cartesian_hole_positions()
        elif not isinstance(HoleCentroids, list) or not isinstance(HoleCentroids, np.ndarray):
            print(f'unknown option for HoleCentroids supplied: type {type(HoleCentroids)}, value: {HoleCentroids}')
        self._check_input_data()
        if ReferenceCrosshairRadius is not None:
            self._generate_reference_crosshair()

        # Methods:
        self._draw_slice_rectangle()
        self._drill_holes()

        # update geometry and view:
        FreeCAD.Gui.ActiveDocument.ActiveView.setAxisCross(True)
        doc.recompute()
        FreeCAD.Gui.SendMsgToActiveView("ViewFit")

    def draw_DSV(self):
        """

        """
        DSV = doc.addObject("Part::Sphere", "DSV")
        DSV.Radius = self.DSV
        DSV.ViewObject.ShapeColor = (0.05, 0.01, 0.0)
        DSV.ViewObject.Transparency = 80

    def draw_Load(self):
        """
        Draw the load. To assist in visualisation.
        """
        if self.LoadRegion is not None:

            if self.LoadRegion['shape'].lower() == 'cylinder':
                Load = doc.addObject("Part::Cylinder", "LoadRegion")
                Load.Radius = self.LoadRegion['radius']
                Load.Height = self.LoadRegion['height']
                Zpos = -1 * self.LoadRegion['height'] / 2  # centered
                Load.Placement = FreeCAD.Placement(FreeCAD.Vector(0, 0, Zpos),
                                                   FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), 0),
                                                   FreeCAD.Vector(0, 0, 0))
                Load.ViewObject.ShapeColor = (.3, .2, .7, 1.0)
            elif self.LoadRegion['shape'].lower() == 'sphere':
                Load = doc.addObject("Part::Sphere", "LoadRegion")
                Load.Radius = self.LoadRegion['radius']
                Load.Placement = FreeCAD.Placement(FreeCAD.Vector(0, 0, 0),
                                                   FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), 0),
                                                   FreeCAD.Vector(0, 0, 0))
                Load.ViewObject.ShapeColor = (.3, .2, .7, 1.0)

        else:
            print(f'You tried to draw a load region, but no load is specified!')

    def draw_Guide(self):
        Guide = doc.addObject("Part::Cylinder", "Guide")
        Guide.Radius = self.GuideRods['radius']
        Guide.Height = self.GuideRods['height']

        Zpos = -1 * self.GuideRods['height'] / 2  # centered
        Xpos = self.HVL_x - self.GuideRods['position']
        Ypos = self.HVL_x - self.GuideRods['position']
        Guide.Placement = FreeCAD.Placement(FreeCAD.Vector(Xpos, Ypos, Zpos),
                                            FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), 0),
                                            FreeCAD.Vector(0, 0, 0))

        # mirror the rods
        Guide = Draft.make_polar_array(Guide, number=4, angle=360.0, center=FreeCAD.Vector(0.0, 0.0, 0.0),
                                       use_link=True)
        Guide.Label = 'GuideRods'

    def _calculate_hole_start(self):
        """
        Figure out where to start drawing the holes. If load region is none it's zero, otherwise need to ensure
        no overlap
        """
        
        # Hole start position with load region
        if self.LoadRegion is None:
            start_load = 0
        elif self.LoadRegion['shape'] == 'cylinder':
            if abs(self.z_pos) < self.LoadRegion['height'] / 2:
                start_load = self.LoadRegion['radius'] + 10
            else:
                start_load = 0
        elif self.LoadRegion['shape'] == 'sphere':
            print('WARNING have not coded hole start properly for spherical loads yet')
            start_load = self.LoadRegion['radius'] + 10
        elif self.LoadRegion['shape'] == 'rectangle':
            if abs(self.z_pos) < self.LoadRegion['height'] / 2:
                start_load = np.sqrt(2 * ((self.LoadRegion['width'] / 2) ** 2)) + 10
            else:
                start_load = 0
                
        # Hole start position with reference crosshair
        start_crosshair = 0
        if self.ReferenceCrosshairRadius is not None:
            start_crosshair = self.ReferenceCrosshairRadius + 10
            
        # Use whichever if larger
        if start_crosshair > start_load:
            self.hole_start = start_crosshair
        else:
            self.hole_start = start_load

    def _calculate_hole_stop(self):
        """
        try and figure out how where to stop drilling the holes
        """
        stop = np.min([self.HVL_x, self.HVL_Y])
        stop = stop - self.hole_spacing / 3
        self.hole_stop = stop

    def add_full_scale_drawing(self):
        """
        Add a basic drawing of the phantom that can be printed off and used to manually drill the holes

        ToDo:: Figure out which paper size needs to be used depending on phantom size
        """

        Page = doc.addObject('TechDraw::DrawPage', 'RealScaleDrawing')
        doc.addObject('TechDraw::DrawSVGTemplate', 'Template')
        this_directory = Path(__file__).parent
        doc.Template.Template = str(this_directory / "../__resources/A2_Landscape_blank.svg")
        Page.Template = doc.Template

        View = doc.addObject('TechDraw::DrawViewPart', 'View')
        Page.addView(View)
        View.Direction = FreeCAD.Vector(0.000, 0.000, -1.000)
        View.Source = [self.ArrayCut]
        View.Scale = 1.0
        View.ViewObject.ArcCenterMarks = True
        View.ViewObject.CenterScale = 3.5
        View.recompute()

    def _check_input_data(self):
        """
        Put any paramter tests here
        """
        if self.HoleCentroids is not None:
            assert isinstance(self.HoleCentroids, (list, np.ndarray))
            assert np.shape(self.HoleCentroids)[0] == 2

        if self.LoadRegion is not None:
            assert (self.LoadRegion['shape'] == 'sphere') or (self.LoadRegion['shape'] == 'cylinder') \
                   or (self.LoadRegion['shape'] == 'rectangle')

    def _draw_slice_rectangle(self):

        SliceBase = doc.addObject("Part::Box", "Box")
        SliceBase.Length = self.HVL_x * 2
        SliceBase.Width = self.HVL_Y * 2
        SliceBase.Height = self.slice_thickness
        SliceBase.Placement = FreeCAD.Placement(FreeCAD.Vector(-self.HVL_x, -self.HVL_Y, 0),
                                                FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), 0),
                                                FreeCAD.Vector(0, 0, 0))

        # add in an etch where the center of the marker will sit (half way down the hole)
        OuterEtch = doc.addObject("Part::Box", "Box")
        OuterEtch.Length = self.HVL_x * 2
        OuterEtch.Width = self.HVL_Y * 2
        OuterEtch.Height = 1
        OuterEtch.Placement = FreeCAD.Placement(FreeCAD.Vector(-self.HVL_x, -self.HVL_Y, self.hole_depth / 2 - .5),
                                                FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), 0),
                                                FreeCAD.Vector(0, 0, 0))

        InnerEtch = doc.addObject("Part::Box", "Box")
        InnerEtch.Length = (self.HVL_x * 2) - 2
        InnerEtch.Width = (self.HVL_Y * 2) - 2
        InnerEtch.Height = 1
        InnerEtch.Placement = FreeCAD.Placement(
            FreeCAD.Vector(-self.HVL_x + 1, -self.HVL_Y + 1, self.hole_depth / 2 - .5),
            FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), 0),
            FreeCAD.Vector(0, 0, 0))
        # Create the EtchCut
        EtchCut = doc.addObject("Part::Cut", "Cut001")
        EtchCut.Base = OuterEtch
        EtchCut.Tool = InnerEtch

        # Subtract the etch cut from the slice base
        SliceBase2 = doc.addObject("Part::Cut", "SliceBase")
        SliceBase2.Base = SliceBase
        SliceBase2.Tool = EtchCut

        # add etches to Z planes
        Z_plane_Etch = doc.addObject("Part::Box", "Box")
        Z_plane_Etch.Length = 1
        Z_plane_Etch.Width = 1
        Z_plane_Etch.Height = 1000  # this is simple intended to be a much longer numver than the user will be likely to request
        Z_plane_Etch.Placement = FreeCAD.Placement(FreeCAD.Vector(self.HVL_x - 1, 0, -500),
                                                   FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), 0),
                                                   FreeCAD.Vector(0, 0, 0))
        # mirror this etch
        Z_plane_Etch_mirror = Draft.make_polar_array(Z_plane_Etch, number=4, angle=360.0,
                                                     center=FreeCAD.Vector(0.0, 0.0, 0.0), use_link=True)
        # now subtract this object:
        EtchCut = doc.addObject("Part::Cut", "ZplaneEtch")
        EtchCut.Base = SliceBase2
        EtchCut.Tool = Z_plane_Etch_mirror

        SliceBase2 = EtchCut

        # add in an etch to indicate radii of interest
        if self.DSV:

            if self._roi_on_marker_center > 0:
                a = np.sqrt((2 * self._roi_on_marker_center * self.DSV) - (self._roi_on_marker_center ** 2))
                OuterCyl = doc.addObject("Part::Cylinder", "Cylinder")
                OuterCyl.Radius = a
                OuterCyl.Height = 1
                InnerCyl = doc.addObject("Part::Cylinder", "Cylinder")
                InnerCyl.Radius = a - 1
                InnerCyl.Height = 1
                EtchCut2 = doc.addObject("Part::Cut", "SliceBase")
                EtchCut2.Base = OuterCyl
                EtchCut2.Tool = InnerCyl

                SliceBase3 = doc.addObject("Part::Cut", "SliceBase")
                SliceBase3.Base = SliceBase2
                SliceBase3.Tool = EtchCut2
                self.SliceBase = SliceBase3  # keep this for drilling holes in
            else:
                self.SliceBase = SliceBase2
        else:
            self.SliceBase = SliceBase2


        if (self.LoadRegion is not None) and (self.ReferenceCrosshairRadius is None):
            self._cut_away_load_region()

        if self.GuideRods is not None:
            self._cut_away_guide_rods()

    def _cut_away_guide_rods(self):
        Guide = doc.addObject("Part::Cylinder", "Guide")
        Guide.Radius = self.GuideRods['radius']
        Guide.Height = self.GuideRods['height']

        Zpos = -1 * self.GuideRods['height'] / 2  # centered
        Xpos = self.HVL_x - self.GuideRods['position']
        Ypos = self.HVL_x - self.GuideRods['position']
        Guide.Placement = FreeCAD.Placement(FreeCAD.Vector(Xpos, Ypos, Zpos),
                                            FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), 0),
                                            FreeCAD.Vector(0, 0, 0))

        # mirror the rods
        Guide = Draft.make_polar_array(Guide, number=4, angle=360.0, center=FreeCAD.Vector(0.0, 0.0, 0.0),
                                       use_link=True)

        CutSlice = doc.addObject("Part::Cut", "Cut")
        CutSlice.Base = self.SliceBase
        CutSlice.Tool = Guide

        self.SliceBase = CutSlice

    def _cut_away_load_region(self):
        """
        Cut the load from each slice and update self.SliceBase

        Because this operation happens before the slice has moved into it's final Z position,
        we move the cylinder instead
        """

        if self.LoadRegion['shape'] == 'cylinder':
            Load = doc.addObject("Part::Cylinder", "Load")
            Load.Radius = self.LoadRegion['radius']
            Load.Height = self.LoadRegion['height']

            Zpos = -1 * self.LoadRegion['height'] / 2  # centered
            Zpos = Zpos - self.z_pos
            if 'z_offset' in self.LoadRegion.keys():
                Zpos = Zpos + self.LoadRegion['z_offset']
            Load.Placement = FreeCAD.Placement(FreeCAD.Vector(0, 0, Zpos),
                                               FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), 0),
                                               FreeCAD.Vector(0, 0, 0))

            CutSlice = doc.addObject("Part::Cut", "Cut")
            CutSlice.Base = self.SliceBase
            CutSlice.Tool = Load
        elif self.LoadRegion['shape'] == 'sphere':
            Load = doc.addObject("Part::Sphere", "Load")
            Load.Radius = self.LoadRegion['radius']

            Load.Placement = FreeCAD.Placement(FreeCAD.Vector(0, 0, 0),
                                               FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), 0),
                                               FreeCAD.Vector(0, 0, 0))
            CutSlice = doc.addObject("Part::Cut", "Cut")
            CutSlice.Base = self.SliceBase
            CutSlice.Tool = Load
        elif self.LoadRegion['shape'] == 'rectangle':
            Load = doc.addObject("Part::Box", "Load")
            Load.Height = self.LoadRegion['height']
            Load.Width = self.LoadRegion['width']
            Load.Length = self.LoadRegion['width']
            Zpos = -1 * self.LoadRegion['height'] / 2  # centered
            Zpos = Zpos - self.z_pos
            if 'z_offset' in self.LoadRegion.keys():
                Zpos = Zpos + self.LoadRegion['z_offset']
            Load.Placement = FreeCAD.Placement(FreeCAD.Vector(-1 * self.LoadRegion['width'] / 2,
                                                              -1 * self.LoadRegion['width'] / 2,
                                                              Zpos),
                                               FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), 0),
                                               FreeCAD.Vector(0, 0, 0))
            CutSlice = doc.addObject("Part::Cut", "Cut")
            CutSlice.Base = self.SliceBase
            CutSlice.Tool = Load

        self.SliceBase = CutSlice

    def _generate_reference_crosshair(self):
        """
        Adds a crosshair shape to a slice up the input size
        """
        
        ReferenceX = []
        ReferenceY = []
        
        # Add central marker
        ReferenceX.append(0)
        ReferenceY.append(0)

        # Add crosshairs markers, starting from center outwards
        r = self.hole_spacing
        
        # If the input size is too small, make it so that there is at least one iteration
        if self.ReferenceCrosshairRadius < r:
            self.ReferenceCrosshairRadius = r
        
        while r <= self.ReferenceCrosshairRadius:
            # +x   
            ReferenceX.append(r)
            ReferenceY.append(0)
            # -x
            ReferenceX.append(-r)
            ReferenceY.append(0)
            # +y
            ReferenceX.append(0)
            ReferenceY.append(r)
            # -y      
            ReferenceX.append(0)
            ReferenceY.append(-r)

            r += self.hole_spacing
                
        self.ReferenceCentroids = [ReferenceX, ReferenceY]
        try:
            self.HoleCentroids[0].extend(ReferenceX)
            self.HoleCentroids[1].extend(ReferenceY)
        except AttributeError:
            # dont think it should be possible that HoleCentroids dont exist but just in case
            self.HoleCentroids = []
            self.HoleCentroids.append(ReferenceY)
            self.HoleCentroids.append(ReferenceX)

    def _generate_roi_polar_hole_positions(self):
        """
        If ROI_polar is chosen as the hole position option, generate holes such the surface of the ROI is well
        covered. This will attemp to
        """

        if self.DSV is None:
            print('cannot determine polar grid without a DSV being specified...application will crash...')
            return
        AllX = []
        AllY = []

        RadialCoordinates = np.linspace(0, self.hole_stop, round(self.hole_stop / self.hole_spacing))
        # we will filter out hole_start and hole_stop below
        if self._roi_on_marker_center > 0:  # move grid to ensure overlap with DSV position
            offset = self._roi_radius_center - RadialCoordinates[
                np.argmin(np.abs(self._roi_on_marker_center - RadialCoordinates))]
            # offset = self._roi_radius_surface -        RadialCoordinates[np.argmin(np.abs(self._roi_on_surface -       RadialCoordinates))]
            RadialCoordinates = RadialCoordinates + offset
        # delete any outside hole_start / stop
        RadialCoordinates = RadialCoordinates[
            np.logical_and(RadialCoordinates > self.hole_start, RadialCoordinates < self.hole_stop)]
        for r in RadialCoordinates:
            circumference = 2 * np.pi * r
            Nmarkers = int((circumference / self.hole_spacing) + 0.5)
            if r == 0 or Nmarkers == 0:
                x = np.array([0])
                y = np.array([0])
            else:
                try:
                    theta = np.linspace(0, (2 * np.pi) - ((2 * np.pi) / Nmarkers), Nmarkers)
                except ZeroDivisionError:
                    print(f'what the devil! {Nmarkers}')
                x = r * np.cos(theta)
                y = r * np.sin(theta)
                self._n_markers = self._n_markers + len(x)
                if abs(r - self._roi_radius_center) < 2:
                    self._n_markers_on_dsv = len(x)
            AllX.extend(x.astype(list))
            AllY.extend(y.astype(list))
        self.HoleCentroids = [AllX, AllY]
        if self._n_markers_on_dsv is None:
            self._n_markers_on_dsv = 0
            print(f'\n\nNO MARKERS FOUND. roi_radius: {self._roi_radius_center}, all r: {RadialCoordinates},'
                  f'z_pos is {self.z_pos}')

    def _generate_cartesian_hole_positions(self):

        NholesY = round((((self.hole_stop)) - self.hole_spacing) / self.hole_spacing)
        NHolesX = round((((self.hole_stop)) - self.hole_spacing) / self.hole_spacing)
        x_half = np.linspace(0, self.hole_stop, NHolesX)
        y_half = np.linspace(0, self.hole_stop, NholesY)
        x = np.unique(np.stack([-1 * np.flip(x_half), x_half]))
        y = np.unique(np.stack([-1 * np.flip(y_half), y_half]))
        [AllX, AllY] = np.meshgrid(x, y)
        AllX = AllX.flatten()
        AllY = AllY.flatten()
        ind_remove_less_than_x = abs(AllX) < self.hole_start
        ind_remove_less_than_y = abs(AllY) < self.hole_start
        ind_remove = np.logical_and(ind_remove_less_than_y, ind_remove_less_than_x)
        # ind_remove_more_than= np.logical_and(abs(AllX) > self.hole_stop, abs(AllY) > self.hole_stop)
        # ind_remove = np.logical_or(ind_remove_more_than, ind_remove_less_than)
        AllX = AllX[np.logical_not(ind_remove)]
        AllY = AllY[np.logical_not(ind_remove)]
        self._n_markers = len(AllY)
        self.HoleCentroids = [AllX, AllY]

    def _drill_holes(self, hole_position_list=None):
        """
        Use locations defined in HoleCentroids to drill holes
        """
        
        if hole_position_list == None:
            hole_position_list = self.HoleCentroids

        # Create objects in two for loops
        CompoundObjectList = []
        for x_pos, y_pos in zip(hole_position_list[0], hole_position_list[1]):
            Cyl = doc.addObject("Part::Cylinder", "Cylinder")
            Cyl.Height = self.hole_depth
            Cyl.Radius = self.hole_radius

            Cyl.Placement = FreeCAD.Placement(FreeCAD.Vector(x_pos + self.GridOffset, y_pos + self.GridOffset, 0),
                                              FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), 0),
                                              FreeCAD.Vector(0, 0, 0))

            CompoundObjectList.append(Cyl)

        Compound = doc.addObject("Part::Compound", "AllHoles")
        Compound.Links = CompoundObjectList

        SliceName = f'Slice_z={self.z_pos}'
        ArrayCut = doc.addObject("Part::Cut", SliceName)
        ArrayCut.Base = self.SliceBase
        ArrayCut.Tool = Compound

        ArrayCut.Placement = FreeCAD.Placement(FreeCAD.Vector(0, 0, (-1 * self.hole_depth / 2) + self.z_pos),
                                               FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), 0),
                                               FreeCAD.Vector(0, 0, 0))
        self.ArrayCut = ArrayCut
        ArrayCut.ViewObject.ShapeColor = (0.4, 0.5, 0.3, 1.0)
        self.SliceBase = self.ArrayCut
