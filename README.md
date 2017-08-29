# Workplane

A small addon which adds a workplane like tool to blender.

The main idea is that it allows for quickly setting up a custom transform orientation, which is used for finding the major two axis the user is viewing - these can then be used as constraints for translate/rotate/scale operations without the need to type it in manually. So for example instead of "g" "Shift-Y" "Shift-Y" you can just do that with one command.

This addon does not recreate the default operations like translate/rotate/scale it merely calls the ones blender offers and sets the constraint axis and transform orientation for you.


Release Log:

0.2: 	
- added toggle to turn off the workplane in the addon-panel 
- added simple draw mode where the workplane just stays where it was originall defined
- added extrude support

0.1:
- initial release


## Usage
Just select something, and hit "set workplane" - a grid will show up, its a visualisation on what plane you would work on if you would start an transform operation.

![overview](https://github.com/BenjaminSauder/Workplane/blob/master/doc/overview.png)

Observe how the workplane adapts to the view - if you like to keep things less flashy hide the workplane or set the draw mode to simple

![view_adapt](https://github.com/BenjaminSauder/Workplane/blob/master/doc/view_adapt.gif)


Here is a mini example, set workplane to polygon, inset face then move the newly inseted face, but as you see it automatically uses the right axis constraints, thus keeps the correct alignement to the polygon. 

![example](https://github.com/BenjaminSauder/Workplane/blob/master/doc/example.gif)

Showing the extrude feature 

![extrude](https://github.com/BenjaminSauder/Workplane/blob/master/doc/extrude.gif)



## Installation
Download a clone as zip from here: [Download ZIP](https://github.com/BenjaminSauder/Workplane/raw/master/release/workplane.zip)

Go to User Preferences > Add-ons > 3D View > Workplane

![enable_addon](https://github.com/BenjaminSauder/Workplane/blob/master/doc/enable_addon.png)

The tools itself is under 3D View > Sidebar Tools > Workplane

![tool_bar](https://github.com/BenjaminSauder/Workplane/blob/master/doc/tool_bar.png)
