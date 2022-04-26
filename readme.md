# MRI_DistortionPhantom



This repository contains code to generate a customized MRI Distortion Phantom in [FreeCAD](https://www.freecadweb.org/). We also provide a 'how to' on manufacturing and imaging such a phantom.

Compared to other MRI distortion phantoms, this work is:

- Free and open source design
- Completely user customizable  
- Water free: light weight and leak free
- Designed for cheap and easy construction



![](docsrc/_resources/PhantomAnimation.gif)


## Setup/Build/Install

- Download and install [FreeCAD](https://www.freecadweb.org/). This work was tested with FreeCAD V0.19. The scripts will be executed within the FreeCAD python environment, so you don't need any additional libraries.
- Clone this repository

## Usage

- For detailed instructions on setting up FreeCAD see HERE.
- From FreeCAD, open the Macro menu and execute FoamPrototypeExample as a macro. 
- All geometric parameters can be altered to your hearts content; detailed instructions on customization are provided here.
- Manufacturing tips are provided HERE.
- Important note: This code is <u>only</u> designed to worked from within FreeCAD. Any attempts to execute it from outside FreeCAD will fail.

## Directory Structure

- **docs** contains html documentation
- **docsrc** markdown/rst source documentation

## Acknowledgements 

This phantom design draws heavily on previous work undertaken at Ingham Institute/ Liverpool Cancer Center on MRI phantom development as described [here](https://aapm.onlinelibrary.wiley.com/doi/pdfdirect/10.1118/1.4915920?casa_token=CcBf93ylYfoAAAAA:yn6h_k-mTRJ2orijpwzfoUtX5zZchs-_qbcifwIP8X6oX2K19QKc7g7_oMXPMyspkzFAdUe-7rqEavzHzQ). 
