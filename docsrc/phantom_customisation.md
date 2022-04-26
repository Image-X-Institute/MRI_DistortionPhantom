# Phantom Customization

The baseline model of a distortion phantom is highly customizable. You can change any of the parameters in the FoamProtoypeExample.py file. One of main reasons you may wish to do this is that different scanner have different field of views, so you may wish to make your phantom larger or smaller.
All options for the AddPhantomSlice class are described within the [code docs](), but we provide some additional notes on some of the more common things you may wish to change below:

## Specifying marker locations 

The marker locations are specified on each slice object. We provide two methods to automatically generate marker locations: ```HoleCentroids=cartesian``` will generate a cartesian grid of markers, while ```ROI_polar```  will generate concentric rings of markers. Both wil the ```hole_spacing``` parameter to space out markers. If you specify a ```DSV```,  the ```ROI_polar``` option will ensure good marker coverage over the surface of this sphere, and will provide an etch of the intersection of the DSV on each slice surface so you can tell where the DSV is on each slice.

You can specify a crosshair of markers using the ```ReferenceCrosshairRadius``` option. This will add a crosshair of markers within ```ReferenceCrosshairRadius```. This is a good idea to add to the central slice, as it makes alignment with CT/Ground truth much easier.

Finally, you may not wish to use any of the existing methods for defining marker positions. In that case, you are free to simply specify them as a list: ```HoleCentroids = [[x1,x2,x3],[y1,y2,y3]]```

## Specifying a load region

This phantom consists of a base material that does not give MRI signal, and is then packed with oil capsules, which also don't generate much signal. This can result in the RF coil of the scanner not being properly loaded. To avoid this, it is a good idea to add some load to your phantom. You can specify a region to be cut from the center of each slice using e.g. ```LoadRegion={'shape': 'rectangle', 'width': 100, 'height': 200}``` (see code docs for other options).

In our experience, not much load is required: during development we simple put a container of oil capsules into a zip lock bag. The exact location of the load also shouldn't be especially sensitive, just put it somewhere near the middle. 

## Specifying a DSV

Specifying a Diameter of Spherical Volume (DSV) has two effects

1. the intersection of the DSV with each slice will be etched on the surface of the slice
2. If you specify ```HoleCentroids=ROI_polar``` then the code will ensure good marker coverage over the surface of the DSV sphere. This can be important if you wish to fit spherical harmonics using this data.

## Specifying Guide Rods

This phantom is based on the concept of individual slices which are stacked on top of each other. A number of methods can be envisaged to hold all of these slices together, but internally we have been using nylon guide rods with great success. 

To specify guide rods, simply use ```GuideRods={'radius': 5, 'position': 30, 'height': 370}```. This will add four holes to the corner of your slice. Each hole will have a radius of` radius` and be  `position` mm from the edge of the slice.

