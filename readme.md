# MRI_DistortionPhantom



This repository contains code to generate a customized MRI Distortion Phantom in [FreeCAD](https://www.freecadweb.org/). We also provide a 'how to' on manufacturing and imaging such a phantom in [our documentation](https://acrf-image-x-institute.github.io/MRI_DistortionPhantom/). For analysis of the phantom images, please see [this repository](https://github.com/ACRF-Image-X-Institute/MRI_DistortionQA)

Compared to other MRI distortion phantoms, this is:

- Free and open source
- Completely user customizable  
- Water free: light weight and leak free
- Designed for cheap and easy construction



![](docsrc/_resources/PhantomAnimation.gif)


## Setup/Build/Install

- Download and install [FreeCAD](https://www.freecadweb.org/). This work was tested with FreeCAD V0.19. The scripts will be executed within the FreeCAD python environment, so you don't need any additional libraries.
- Clone this repository

## Usage

- To generate your first phantom design, please see the [getting started](https://acrf-image-x-institute.github.io/MRI_DistortionPhantom/GettingStarted.html) page in the docs
- Important note: This code is <u>only</u> designed to worked from within FreeCAD. Any attempts to execute it from outside FreeCAD will fail.

## Directory Structure

- **docs** contains html documentation
- **docsrc** markdown/rst source documentation

## Acknowledgements 

This phantom design draws heavily on previous work undertaken at Ingham Institute/ Liverpool Cancer Center on MRI phantom development as described [here](https://aapm.onlinelibrary.wiley.com/doi/pdfdirect/10.1118/1.4915920?casa_token=CcBf93ylYfoAAAAA:yn6h_k-mTRJ2orijpwzfoUtX5zZchs-_qbcifwIP8X6oX2K19QKc7g7_oMXPMyspkzFAdUe-7rqEavzHzQ). 
