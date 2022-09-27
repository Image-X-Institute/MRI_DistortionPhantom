# Getting Started

## Setting up FreeCAD

FreeCAD of course has its [own documentation](https://wiki.freecad.org/Getting_started), which should be your first point of call for any trouble shooting of this program. Here, we provide a basic intro into setting up and configuring freeCAD so that you can build your first phantom. 

1. [Download FreeCAD](https://www.freecadweb.org/downloads.php). This code was developed and tested with version 0.19. Future versions should work, but if you run into issues go with version 0.19
2. Open FreeCAD 
3. In “View” “panels” enable both the python console and the report view. This isn't required, but in my opinion tends to make life easier!
4. After these steps, you should have something that looks like the image below, and are ready to generate your first phantom!

![](_resources/FreeCADsetup.jpg)



## Generating your first phantom design

1. Open the scripting interface using the button in the top right in the figure above (or through the menus, click macro, macros)
2. Navigate to wherever you cloned [this repository](https://github.com/ACRF-Image-X-Institute/MRI_DistortionPhantom) and choose the phantom_designs folder
3. Execute phantom_template.py as a macro (or any of the other designs)
4. That's it! you can open up the  FoamPrototypeExample.py script to see exactly what it's doing, and you can read the section on [customizing the phantom](https://acrf-image-x-institute.github.io/MRI_DistortionPhantom/phantom_customisation.html#) to change this basic design to your hearts desire.

